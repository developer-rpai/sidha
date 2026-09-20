"""Computable phenotypes for HS research.

A phenotype is a versioned, reusable rule that decides whether a patient's
timeline shows a condition. Version every definition (``PHENOTYPE_VERSION``)
so published analyses stay reproducible as the rules evolve.
"""

from __future__ import annotations

from datetime import timedelta

from ..ehr.events import PatientTimeline
from . import codes

PHENOTYPE_VERSION = "2026.09.1"


def _condition_codes(timeline: PatientTimeline, group: str) -> list:
    wanted = codes.group_codes(group)
    return [
        e
        for e in timeline.of_type("condition")
        if e.code_system == "ICD10" and e.code in wanted
    ]


def hs_case(timeline: PatientTimeline, strict: bool = False) -> bool:
    """HS case definition.

    - Standard: at least one L73.2 (hidradenitis suppurativa) condition event.
    - Strict: at least two L73.2 events on distinct dates 30+ days apart,
      reducing rule-out / single-mention false positives.
    """
    events = _condition_codes(timeline, "hs")
    if not events:
        return False
    if not strict:
        return True
    distinct = sorted({e.event_date for e in events})
    return any((b - a) >= timedelta(days=30) for a in distinct for b in distinct if b > a)


def has_comorbidity(timeline: PatientTimeline, group: str) -> bool:
    """True if the timeline contains any condition code in the given group."""
    return bool(_condition_codes(timeline, group))


def comorbidity_profile(timeline: PatientTimeline) -> dict[str, bool]:
    """Presence/absence of each tracked comorbidity group for one patient."""
    groups = [
        "obesity",
        "diabetes_t2",
        "metabolic_syndrome",
        "depression",
        "anxiety",
        "nicotine",
        "crohn",
        "ankylosing_spondylitis",
        "pcos",
    ]
    return {g: has_comorbidity(timeline, g) for g in groups}


def diagnostic_delay_days(timeline: PatientTimeline) -> int | None:
    """Days from first HS-suggestive code to first confirmed HS diagnosis.

    HS-suggestive codes are abscess, acne vulgaris, pilonidal disease, and
    other L73 family codes: the diagnoses HS is most often first coded as
    before the correct L73.2 diagnosis lands. Returns None when no confirmed
    HS diagnosis exists in the timeline.
    """
    hs_dates = [e.event_date for e in _condition_codes(timeline, "hs")]
    if not hs_dates:
        return None
    dx_date = min(hs_dates)
    suggestive: list = []
    for group in ("abscess", "acne_vulgaris", "pilonidal", "hs_family"):
        suggestive.extend(
            e for e in _condition_codes(timeline, group) if e.event_date < dx_date
        )
    if not suggestive:
        return 0
    return (dx_date - min(e.event_date for e in suggestive)).days


def summarize_cohort(timelines: list[PatientTimeline]) -> dict:
    """Cohort-level summary: case counts, strict cases, mean diagnostic delay."""
    cases = [t for t in timelines if hs_case(t)]
    strict = [t for t in timelines if hs_case(t, strict=True)]
    delays = [
        d for t in cases if (d := diagnostic_delay_days(t)) is not None and d > 0
    ]
    return {
        "phenotype_version": PHENOTYPE_VERSION,
        "n_patients": len(timelines),
        "n_hs_cases": len(cases),
        "n_hs_cases_strict": len(strict),
        "n_with_prior_suggestive_codes": len(delays),
        "mean_diagnostic_delay_days": (
            round(sum(delays) / len(delays), 1) if delays else None
        ),
    }
