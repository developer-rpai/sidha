"""Tests for sidha.diagnostics: features, screener, differential ranking,
and misdiagnosis reports.

All fixtures are synthetic — no real patient data anywhere.
"""

from datetime import date, timedelta

import pytest

from sidha.clinical.phenotypes import hs_case
from sidha.datasets.synthetic import generate_cohort
from sidha.diagnostics import (
    FEATURE_DESCRIPTIONS,
    FEATURE_NAMES,
    EarlyDetectionScreener,
    auc,
    evaluate,
    extract_features,
    feature_matrix,
    misdiagnosis_report,
    rank_differentials,
    threshold_sweep,
)
from sidha.ehr.events import ClinicalEvent, PatientTimeline, build_timelines


def _hs_timelines(n: int = 30, seed: int = 7) -> list[PatientTimeline]:
    events = generate_cohort(n_patients=n, seed=seed)
    return list(build_timelines(events).values())


def _control_timeline(pid: str, n_abscess: int = 1) -> PatientTimeline:
    """A non-HS timeline: isolated abscess(es), no HS trajectory."""
    tl = PatientTimeline(pid)
    base = date(2020, 3, 1)
    for i in range(n_abscess):
        tl.add(
            ClinicalEvent(
                pid,
                base + timedelta(days=i * 400),
                "condition",
                "L02.9",
                "ICD10",
                "Cutaneous abscess",
            )
        )
    return tl


def _empty_timeline() -> PatientTimeline:
    return PatientTimeline("EMPTY-1")


# ---------------------------------------------------------------- features


def test_feature_names_match_descriptions():
    assert set(FEATURE_NAMES) == set(FEATURE_DESCRIPTIONS)
    assert len(FEATURE_NAMES) == 10


def test_extract_features_hs_patient():
    tl = _hs_timelines(1, seed=11)[0]
    feats = extract_features(tl)
    assert set(feats) == set(FEATURE_NAMES)
    # Generator emits 2-6 pre-diagnosis encounters, each an abscess, acne, or
    # pilonidal code; the total is the deterministic invariant.
    total_suggestive = (
        feats["abscess_events"] + feats["acne_events"] + feats["pilonidal_events"]
    )
    assert total_suggestive >= 2
    assert feats["distinct_suggestive_groups"] >= 1
    assert feats["years_since_first_symptom"] > 1.0  # 1-9y delay + post-dx events
    assert all(v >= 0 for v in feats.values())


def test_extract_features_empty_timeline():
    feats = extract_features(_empty_timeline())
    assert feats["abscess_events"] == 0.0
    assert feats["distinct_suggestive_groups"] == 0.0
    assert feats["years_since_first_symptom"] == 0.0
    assert feats["early_onset"] == 0.0


def test_early_onset_requires_birth_year():
    tl = _hs_timelines(1, seed=11)[0]
    assert extract_features(tl)["early_onset"] == 0.0  # unknown -> 0.0
    assert extract_features(tl, birth_year=1995)["early_onset"] == 1.0
    assert extract_features(tl, birth_year=1950)["early_onset"] == 0.0


def test_recurrent_skin_infections_flag():
    tl = _control_timeline("C-1", n_abscess=3)
    assert extract_features(tl)["recurrent_skin_infections"] == 1.0
    tl2 = _control_timeline("C-2", n_abscess=2)
    assert extract_features(tl2)["recurrent_skin_infections"] == 0.0


def test_feature_matrix_order_and_ids():
    tls = _hs_timelines(3, seed=5)
    rows, ids = feature_matrix(tls)
    assert ids == [t.patient_id for t in tls]
    assert len(rows) == 3 and all(len(r) == len(FEATURE_NAMES) for r in rows)
    # Matrix row matches the dict extraction, in FEATURE_NAMES order.
    feats = extract_features(tls[0])
    assert rows[0] == [feats[n] for n in FEATURE_NAMES]


# ---------------------------------------------------------------- screener


def test_reference_screener_scores_hs_high_and_control_low():
    s = EarlyDetectionScreener()
    assert not s.fitted
    hs_score = s.score(_hs_timelines(1, seed=21)[0])
    ctrl_score = s.score(_control_timeline("C-9", n_abscess=1))
    empty_score = s.score(_empty_timeline())
    assert hs_score > 0.5 > ctrl_score
    assert empty_score < 0.3


def test_screener_predict_threshold():
    s = EarlyDetectionScreener(threshold=0.9)
    tl = _hs_timelines(1, seed=21)[0]
    assert s.predict(tl, threshold=0.1)
    assert isinstance(s.predict(tl), bool)


def test_screener_score_batch_preserves_order():
    s = EarlyDetectionScreener()
    tls = _hs_timelines(4, seed=3)
    scores = s.score_batch(tls)
    assert len(scores) == 4
    assert all(0.0 <= x <= 1.0 for x in scores)
    assert scores[0] == s.score(tls[0])


def test_feature_contributions_sorted_and_explainable():
    s = EarlyDetectionScreener()
    contribs = s.feature_contributions(_hs_timelines(1, seed=21)[0])
    assert [n for n, _ in contribs] and len(contribs) == len(FEATURE_NAMES)
    mags = [abs(v) for _, v in contribs]
    assert mags == sorted(mags, reverse=True)
    top = contribs[0][0]
    assert top in (
        "abscess_events",
        "recurrent_skin_infections",
        "years_since_first_symptom",
        "distinct_suggestive_groups",
    )


def test_fit_calibrates_and_separates():
    hs = _hs_timelines(20, seed=42)
    ctrls = [_control_timeline(f"C-{i}", n_abscess=1) for i in range(20)]
    timelines = hs + ctrls
    labels = [1] * 20 + [0] * 20
    s = EarlyDetectionScreener().fit(timelines, labels)
    assert s.fitted
    metrics = evaluate(s, timelines, labels)
    assert metrics["auc"] is not None and metrics["auc"] > 0.8
    assert metrics["tp"] + metrics["tn"] + metrics["fp"] + metrics["fn"] == 40


def test_fit_validation_errors():
    s = EarlyDetectionScreener()
    tls = _hs_timelines(3, seed=1)
    with pytest.raises(ValueError):
        s.fit(tls, [1, 1])  # misaligned
    with pytest.raises(ValueError):
        s.fit(tls, [1, 1, 1])  # single class


def test_evaluate_metric_keys_and_sanity():
    s = EarlyDetectionScreener()
    tls = _hs_timelines(6, seed=8)
    metrics = evaluate(s, tls, [1] * 6)
    for key in ("accuracy", "sensitivity", "specificity", "ppv", "npv",
                "auc", "tp", "tn", "fp", "fn", "threshold", "n"):
        assert key in metrics
    assert metrics["n"] == 6
    assert metrics["auc"] is None  # single class
    assert metrics["sensitivity"] == 1.0  # all HS, reference weights


def test_auc_perfect_and_worst():
    assert auc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1]) == 1.0
    assert auc([1, 1, 0, 0], [0.1, 0.2, 0.8, 0.9]) == 0.0
    assert auc([1, 1], [0.5, 0.6]) is None


def test_threshold_sweep_shape():
    s = EarlyDetectionScreener()
    tls = _hs_timelines(4, seed=2) + [_control_timeline(f"C-{i}") for i in range(4)]
    sweep = threshold_sweep(s, tls, [1] * 4 + [0] * 4, steps=5)
    assert len(sweep) == 5
    assert [m["threshold"] for m in sweep] == [0.0, 0.25, 0.5, 0.75, 1.0]


# ------------------------------------------------------------- differential


def test_hs_ranks_first_for_classic_case():
    ranked = rank_differentials(_hs_timelines(1, seed=21)[0])
    assert ranked[0].name == "Hidradenitis suppurativa"
    assert ranked[0].supporting  # reasons are populated
    scores = [c.score for c in ranked]
    assert scores == sorted(scores, reverse=True)


def test_single_abscess_favors_simple_abscess():
    ranked = rank_differentials(_control_timeline("C-1", n_abscess=1))
    top = ranked[0]
    assert top.name == "Cutaneous abscess / furuncle"
    hs = next(c for c in ranked if c.name == "Hidradenitis suppurativa")
    assert hs.score < top.score


def test_crohns_patient_surfaces_fistulizing_crohns():
    tl = _control_timeline("C-CD", n_abscess=2)
    tl.add(ClinicalEvent("C-CD", date(2019, 5, 1), "condition",
                         "K50.90", "ICD10", "Crohn's disease"))
    ranked = rank_differentials(tl)
    cd = next(c for c in ranked if c.name == "Fistulizing Crohn's disease")
    ab = next(c for c in ranked if c.name == "Cutaneous abscess / furuncle")
    assert cd.score > ab.score
    assert cd.supporting


def test_ranking_is_deterministic():
    tl = _hs_timelines(1, seed=33)[0]
    first = [c.name for c in rank_differentials(tl)]
    second = [c.name for c in rank_differentials(tl)]
    assert first == second
    assert len(first) == 6


# ------------------------------------------------------------- misdiagnosis


def test_misdiagnosis_report_on_synthetic_cohort():
    tls = _hs_timelines(25, seed=99)
    rep = misdiagnosis_report(tls)
    assert rep["n_cases"] == 25
    assert rep["n_excluded"] == 0
    assert rep["phenotype_version"]
    assert "L02.9" in rep["codes"]  # abscess dominates pre-dx coding
    top_code = next(iter(rep["codes"]))
    assert rep["codes"][top_code]["share"] > 0.5
    assert rep["median_delay_days_overall"] is not None
    assert rep["median_delay_days_overall"] > 300
    assert rep["common_first_codes"]


def test_misdiagnosis_report_excludes_non_cases():
    tls = _hs_timelines(5, seed=4) + [_control_timeline(f"C-{i}") for i in range(3)]
    rep = misdiagnosis_report(tls)
    assert rep["n_cases"] == 5
    assert rep["n_excluded"] == 3


def test_misdiagnosis_report_empty_cohort():
    rep = misdiagnosis_report([])
    assert rep["n_cases"] == 0
    assert rep["codes"] == {}
    assert rep["median_delay_days_overall"] is None


def test_report_consistent_with_phenotype_delay():
    tls = _hs_timelines(10, seed=13)
    rep = misdiagnosis_report(tls)
    from sidha.clinical.phenotypes import diagnostic_delay_days
    delays = [d for t in tls if (d := diagnostic_delay_days(t)) and d > 0]
    assert rep["n_cases"] == sum(1 for t in tls if hs_case(t))
    assert delays  # sanity: the fixture really has delays
