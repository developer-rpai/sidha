"""Early-detection screener: transparent HS-risk scoring from EHR patterns.

``EarlyDetectionScreener`` is a logistic-style classifier over the feature
vector from :mod:`sidha.diagnostics.features`. It is a **research reference
implementation**, not a diagnostic device:

- ``REFERENCE_WEIGHTS`` / ``REFERENCE_INTERCEPT`` are illustrative defaults
  shaped by published associations (recurrent abscess coding, diagnostic
  delays of several years, HS comorbidity patterns). They were **not** fitted
  on real patient data and must not be used clinically.
- ``fit()`` calibrates weights on a caller-supplied labeled cohort using
  plain batch gradient descent (stdlib only, L2 regularization), so research
  groups can train the same architecture on their own data.
- ``evaluate()`` reports accuracy, sensitivity, specificity, PPV, NPV, and
  AUC at a chosen threshold.

No output of this module is medical advice.
"""

from __future__ import annotations

import math

from ..ehr.events import PatientTimeline
from .features import FEATURE_NAMES, extract_features, feature_matrix

# Illustrative reference weights, shaped by published associations:
# recurrent abscess/furuncle coding and multi-year diagnostic odysseys carry
# the strongest signal; comorbidity burden and utilization density are weaker
# but directionally positive. NOT fitted on real patient data.
REFERENCE_WEIGHTS: dict[str, float] = {
    "abscess_events": 0.55,
    "acne_events": 0.20,
    "pilonidal_events": 0.35,
    "other_hs_family_events": 0.45,
    "distinct_suggestive_groups": 0.30,
    "comorbidity_count": 0.25,
    "conditions_per_year": 0.10,
    "recurrent_skin_infections": 0.60,
    "years_since_first_symptom": 0.12,
    "early_onset": 0.40,
}
REFERENCE_INTERCEPT: float = -2.6


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def auc(labels: list[int], scores: list[float]) -> float | None:
    """Area under the ROC curve via the Mann-Whitney U statistic.

    Returns None when the labels contain only one class.
    """
    if len(set(labels)) < 2:
        return None
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 4)


class EarlyDetectionScreener:
    """Transparent logistic-style screener for pre-diagnosis HS risk.

    Scores a patient timeline in [0, 1]; higher means more HS-suggestive
    EHR patterns. Construct with reference weights, or call :meth:`fit`
    on a labeled cohort to calibrate weights to your own data.
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        intercept: float = REFERENCE_INTERCEPT,
        threshold: float = 0.5,
    ) -> None:
        self.weights = dict(weights if weights is not None else REFERENCE_WEIGHTS)
        missing = set(FEATURE_NAMES) - set(self.weights)
        if missing:
            raise ValueError(f"weights missing features: {sorted(missing)}")
        self.intercept = intercept
        self.threshold = threshold
        self.fitted = weights is not None

    def _logit(self, feats: dict[str, float]) -> float:
        return self.intercept + sum(
            self.weights[name] * feats[name] for name in FEATURE_NAMES
        )

    def score(
        self,
        timeline: PatientTimeline,
        birth_year: int | None = None,
    ) -> float:
        """Risk score in [0, 1] for one patient timeline."""
        return _sigmoid(self._logit(extract_features(timeline, birth_year)))

    def score_batch(
        self,
        timelines: list[PatientTimeline],
        demographics: dict[str, dict] | None = None,
    ) -> list[float]:
        """Score a cohort, preserving order."""
        demographics = demographics or {}
        return [
            self.score(tl, demographics.get(tl.patient_id, {}).get("birth_year"))
            for tl in timelines
        ]

    def predict(
        self,
        timeline: PatientTimeline,
        birth_year: int | None = None,
        threshold: float | None = None,
    ) -> bool:
        """Binary screen at ``threshold`` (default: the instance threshold)."""
        return self.score(timeline, birth_year) >= (
            self.threshold if threshold is None else threshold
        )

    def feature_contributions(
        self,
        timeline: PatientTimeline,
        birth_year: int | None = None,
    ) -> list[tuple[str, float]]:
        """Per-feature logit contributions, largest first (explainability)."""
        feats = extract_features(timeline, birth_year)
        contribs = [
            (name, self.weights[name] * feats[name]) for name in FEATURE_NAMES
        ]
        return sorted(contribs, key=lambda kv: abs(kv[1]), reverse=True)

    def fit(
        self,
        timelines: list[PatientTimeline],
        labels: list[int],
        demographics: dict[str, dict] | None = None,
        learning_rate: float = 0.05,
        l2: float = 0.01,
        max_iter: int = 2000,
        tol: float = 1e-6,
    ) -> "EarlyDetectionScreener":
        """Calibrate weights on a labeled cohort (batch gradient descent).

        Args:
            timelines: patient timelines.
            labels: 1 for HS case, 0 for control, aligned with ``timelines``.
            demographics: optional patient_id -> {"birth_year": int}.
            learning_rate: gradient step size.
            l2: L2 regularization strength.
            max_iter: maximum gradient steps.
            tol: stop when max |weight change| < tol.

        Returns:
            self, with fitted weights; ``self.fitted`` becomes True.
        """
        if len(timelines) != len(labels):
            raise ValueError("timelines and labels must align")
        if len(set(labels)) < 2:
            raise ValueError("need both classes to fit")

        X, _ = feature_matrix(timelines, demographics)
        n = len(X)
        w = [0.0] * len(FEATURE_NAMES)
        b = 0.0

        for _ in range(max_iter):
            grads = [0.0] * len(FEATURE_NAMES)
            grad_b = 0.0
            for row, y in zip(X, labels):
                p = _sigmoid(b + sum(wi * xi for wi, xi in zip(w, row)))
                err = p - y
                grad_b += err
                for j, xj in enumerate(row):
                    grads[j] += err * xj
            max_change = 0.0
            for j in range(len(w)):
                g = grads[j] / n + l2 * w[j]
                step = learning_rate * g
                w[j] -= step
                max_change = max(max_change, abs(step))
            b -= learning_rate * grad_b / n
            max_change = max(max_change, abs(learning_rate * grad_b / n))
            if max_change < tol:
                break

        self.weights = dict(zip(FEATURE_NAMES, (round(v, 4) for v in w)))
        self.intercept = round(b, 4)
        self.fitted = True
        return self


def evaluate(
    screener: EarlyDetectionScreener,
    timelines: list[PatientTimeline],
    labels: list[int],
    demographics: dict[str, dict] | None = None,
    threshold: float | None = None,
) -> dict:
    """Score a labeled cohort and report classification metrics.

    Returns accuracy, sensitivity (recall), specificity, PPV, NPV, AUC,
    and the confusion-matrix counts at the given threshold.
    """
    scores = screener.score_batch(timelines, demographics)
    thr = screener.threshold if threshold is None else threshold
    preds = [1 if s >= thr else 0 for s in scores]
    tp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 1)
    tn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 0)
    fp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 0)
    fn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 1)

    def _safe(num: int, den: int) -> float | None:
        return round(num / den, 4) if den else None

    return {
        "n": len(labels),
        "threshold": thr,
        "accuracy": _safe(tp + tn, len(labels)),
        "sensitivity": _safe(tp, tp + fn),
        "specificity": _safe(tn, tn + fp),
        "ppv": _safe(tp, tp + fp),
        "npv": _safe(tn, tn + fn),
        "auc": auc(labels, scores),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def threshold_sweep(
    screener: EarlyDetectionScreener,
    timelines: list[PatientTimeline],
    labels: list[int],
    demographics: dict[str, dict] | None = None,
    steps: int = 21,
) -> list[dict]:
    """Evaluate at evenly spaced thresholds; useful for picking an
    operating point (e.g., maximizing Youden's J = sens + spec - 1)."""
    return [
        evaluate(
            screener,
            timelines,
            labels,
            demographics,
            threshold=round(i / (steps - 1), 3),
        )
        for i in range(steps)
    ]
