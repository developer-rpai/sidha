"""diagnostics — diagnostic-support analytics for HS research.

Reference implementations for studying hidradenitis suppurativa's diagnostic
journey in coded EHR data:

- :mod:`sidha.diagnostics.features` — feature extraction from patient
  timelines (recurrent lesion codes, comorbidity burden, timeline density).
- :mod:`sidha.diagnostics.screener` — ``EarlyDetectionScreener``, a
  transparent logistic-style risk scorer for pre-diagnosis HS risk, with
  reference weights and a ``fit()`` method for cohort-specific calibration.
- :mod:`sidha.diagnostics.differential` — evidence-accumulating
  differential-diagnosis ranking with human-readable reasons.
- :mod:`sidha.diagnostics.misdiagnosis` — cohort-level misdiagnosis-pattern
  reports (which codes precede HS, how long the delays are).

Research aids only. Nothing here is a diagnostic device, and no output of
these modules is medical advice. Reference weights are illustrative
defaults shaped by published associations — fit the screener on your own
labeled cohort before any research use.
"""

from sidha.diagnostics import differential, features, misdiagnosis, screener
from sidha.diagnostics.differential import (
    DifferentialCandidate,
    rank_differentials,
)
from sidha.diagnostics.features import (
    FEATURE_DESCRIPTIONS,
    FEATURE_NAMES,
    extract_features,
    feature_matrix,
)
from sidha.diagnostics.misdiagnosis import misdiagnosis_report
from sidha.diagnostics.screener import (
    REFERENCE_INTERCEPT,
    REFERENCE_WEIGHTS,
    EarlyDetectionScreener,
    auc,
    evaluate,
    threshold_sweep,
)

__all__ = [
    "DifferentialCandidate",
    "EarlyDetectionScreener",
    "FEATURE_DESCRIPTIONS",
    "FEATURE_NAMES",
    "REFERENCE_INTERCEPT",
    "REFERENCE_WEIGHTS",
    "auc",
    "differential",
    "evaluate",
    "extract_features",
    "feature_matrix",
    "features",
    "misdiagnosis",
    "misdiagnosis_report",
    "rank_differentials",
    "screener",
    "threshold_sweep",
]
