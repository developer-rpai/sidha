"""Tests for clinical crosswalks, phenotypes, and instruments."""

from __future__ import annotations

from datetime import date

from sidha.clinical import codes, instruments, phenotypes
from sidha.datasets import generate_cohort
from sidha.ehr import ClinicalEvent, PatientTimeline, build_timelines


def _timeline(*coded_dates: tuple[str, str]) -> PatientTimeline:
    t = PatientTimeline("PX")
    for code, iso in coded_dates:
        t.add(ClinicalEvent("PX", date.fromisoformat(iso), "condition", code, "ICD10"))
    return t


def test_code_crosswalks():
    assert codes.describe("L73.2") is not None
    assert codes.describe("ED92.0", system="ICD11") == "Hidradenitis suppurativa"
    assert codes.describe("3723001", system="SNOMED") == "Hidradenitis suppurativa"
    assert "L73.2" in codes.group_codes("hs")


def test_hs_case_standard_and_strict():
    loose = _timeline(("L73.2", "2023-01-20"))
    assert phenotypes.hs_case(loose) is True
    assert phenotypes.hs_case(loose, strict=True) is False
    strict = _timeline(("L73.2", "2023-01-20"), ("L73.2", "2023-03-01"))
    assert phenotypes.hs_case(strict, strict=True) is True
    no_case = _timeline(("L02.9", "2023-01-20"))
    assert phenotypes.hs_case(no_case) is False


def test_diagnostic_delay():
    t = _timeline(
        ("L02.9", "2019-03-14"),
        ("L70.0", "2020-07-02"),
        ("L73.2", "2023-01-20"),
    )
    delay = phenotypes.diagnostic_delay_days(t)
    assert delay == (date(2023, 1, 20) - date(2019, 3, 14)).days
    assert phenotypes.diagnostic_delay_days(_timeline(("L02.9", "2020-01-01"))) is None


def test_comorbidity_profile():
    t = _timeline(("L73.2", "2023-01-20"), ("E66.9", "2020-01-10"), ("F32.9", "2020-05-22"))
    profile = phenotypes.comorbidity_profile(t)
    assert profile["obesity"] is True
    assert profile["depression"] is True
    assert profile["crohn"] is False


def test_hurley_staging():
    assert instruments.hurley_stage(abscesses=True, sinus_tracts=False, scarring=False, diffuse_involvement=False) == "I"
    assert instruments.hurley_stage(abscesses=True, sinus_tracts=True, scarring=True, diffuse_involvement=False) == "II"
    assert instruments.hurley_stage(abscesses=True, sinus_tracts=True, scarring=True, diffuse_involvement=True) == "III"
    assert instruments.hurley_stage(abscesses=False, sinus_tracts=False, scarring=False, diffuse_involvement=False) == "indeterminate"


def test_likert_scoring():
    result = instruments.score_likert_scale([1, 2, 3, None], max_per_item=4, min_answered=3)
    assert result["score"] == round((1 + 2 + 3) / 3 * 4, 2)
    assert result["n_answered"] == 3
    missing = instruments.score_likert_scale([1, None, None, None], max_per_item=4, min_answered=2)
    assert missing["score"] is None


def test_synthetic_cohort_end_to_end():
    events = generate_cohort(n_patients=20, seed=7)
    timelines = build_timelines(events)
    assert len(timelines) == 20
    summary = phenotypes.summarize_cohort(list(timelines.values()))
    assert summary["n_hs_cases"] == 20
    assert summary["phenotype_version"] == phenotypes.PHENOTYPE_VERSION
    assert summary["mean_diagnostic_delay_days"] is not None
    assert summary["mean_diagnostic_delay_days"] > 365


def test_synthetic_is_deterministic():
    a = generate_cohort(n_patients=5, seed=123)
    b = generate_cohort(n_patients=5, seed=123)
    assert a == b
