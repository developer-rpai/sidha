"""Feature extraction for the HS early-detection screener.

Converts a :class:`~sidha.ehr.events.PatientTimeline` into a fixed numeric
feature vector capturing the EHR patterns that published claims-data studies
associate with pre-diagnosis hidradenitis suppurativa: recurrent abscess /
furuncle coding, persistent acne coding, pilonidal disease, other L73-family
codes, comorbidity burden, and timeline density.

Features are deliberately code-level (no anatomy fields exist in the event
model) and explainable: every feature has a one-line description in
``FEATURE_DESCRIPTIONS``.
"""

from __future__ import annotations

from datetime import date

from ..clinical import codes
from ..ehr.events import PatientTimeline

FEATURE_NAMES: list[str] = [
    "abscess_events",
    "acne_events",
    "pilonidal_events",
    "other_hs_family_events",
    "distinct_suggestive_groups",
    "comorbidity_count",
    "conditions_per_year",
    "recurrent_skin_infections",
    "years_since_first_symptom",
    "early_onset",
]

FEATURE_DESCRIPTIONS: dict[str, str] = {
    "abscess_events": "Count of cutaneous abscess/furuncle (L02.9) condition events.",
    "acne_events": "Count of acne vulgaris (L70.0) condition events.",
    "pilonidal_events": "Count of pilonidal disease condition events.",
    "other_hs_family_events": (
        "Count of L73-family condition events other than confirmed HS (L73.2)."
    ),
    "distinct_suggestive_groups": (
        "Number of distinct HS-suggestive code groups present "
        "(abscess, acne, pilonidal, HS family)."
    ),
    "comorbidity_count": (
        "Number of tracked HS-associated comorbidity groups present "
        "(obesity, T2D, metabolic syndrome, depression, anxiety, nicotine, "
        "Crohn's, ankylosing spondylitis, PCOS)."
    ),
    "conditions_per_year": (
        "Condition events per year of timeline span "
        "(care-utilization density; floor of 90 days span)."
    ),
    "recurrent_skin_infections": (
        "1.0 when abscess events >= 3 (recurrence proxy), else 0.0."
    ),
    "years_since_first_symptom": (
        "Years from first HS-suggestive code to the most recent event "
        "(diagnostic-odyssey proxy; 0.0 when no suggestive code)."
    ),
    "early_onset": (
        "1.0 when the first HS-suggestive code appears before age 30 "
        "(requires birth_year); 0.0 when unknown."
    ),
}

_SUGGESTIVE_GROUPS = ("abscess", "acne_vulgaris", "pilonidal", "hs_family")
_COMORBIDITY_GROUPS = (
    "obesity",
    "diabetes_t2",
    "metabolic_syndrome",
    "depression",
    "anxiety",
    "nicotine",
    "crohn",
    "ankylosing_spondylitis",
    "pcos",
)


def _icd10_conditions(timeline: PatientTimeline, group: str) -> list:
    wanted = codes.group_codes(group)
    return [
        e
        for e in timeline.of_type("condition")
        if e.code_system == "ICD10" and e.code in wanted
    ]


def extract_features(
    timeline: PatientTimeline,
    birth_year: int | None = None,
) -> dict[str, float]:
    """Extract the screener feature vector from one patient timeline.

    Args:
        timeline: the patient's chronological event history.
        birth_year: optional birth year, used only for the ``early_onset``
            feature. Falls back to 0.0 when unknown.

    Returns:
        Dict mapping each name in :data:`FEATURE_NAMES` to a float.
    """
    grouped = {g: _icd10_conditions(timeline, g) for g in _SUGGESTIVE_GROUPS}

    abscess_n = len(grouped["abscess"])
    acne_n = len(grouped["acne_vulgaris"])
    pilonidal_n = len(grouped["pilonidal"])
    # L73-family codes other than the confirmed HS diagnosis itself.
    other_hs_family_n = sum(
        1 for e in grouped["hs_family"] if e.code != "L73.2"
    )
    distinct_groups = sum(1 for g, evs in grouped.items() if evs)

    comorbidity_n = sum(
        1 for g in _COMORBIDITY_GROUPS if _icd10_conditions(timeline, g)
    )

    conditions = timeline.of_type("condition")
    if conditions:
        span_days = max(
            (max(e.event_date for e in conditions)
             - min(e.event_date for e in conditions)).days,
            90,
        )
    else:
        span_days = 90
    conditions_per_year = len(conditions) / (span_days / 365.25)

    suggestive_dates = [
        e.event_date for evs in grouped.values() for e in evs
    ]
    if suggestive_dates:
        first_symptom = min(suggestive_dates)
        last_event = max(e.event_date for e in timeline.events)
        years_since = (last_event - first_symptom).days / 365.25
    else:
        first_symptom = None
        years_since = 0.0

    early_onset = 0.0
    if birth_year is not None and first_symptom is not None:
        early_onset = 1.0 if (first_symptom.year - birth_year) < 30 else 0.0

    return {
        "abscess_events": float(abscess_n),
        "acne_events": float(acne_n),
        "pilonidal_events": float(pilonidal_n),
        "other_hs_family_events": float(other_hs_family_n),
        "distinct_suggestive_groups": float(distinct_groups),
        "comorbidity_count": float(comorbidity_n),
        "conditions_per_year": round(conditions_per_year, 4),
        "recurrent_skin_infections": 1.0 if abscess_n >= 3 else 0.0,
        "years_since_first_symptom": round(max(years_since, 0.0), 4),
        "early_onset": early_onset,
    }


def feature_matrix(
    timelines: list[PatientTimeline],
    demographics: dict[str, dict] | None = None,
) -> tuple[list[list[float]], list[str]]:
    """Build (X, patient_ids) for a cohort.

    Args:
        timelines: patient timelines in a fixed order.
        demographics: optional mapping of patient_id -> {"birth_year": int}.

    Returns:
        ``(rows, patient_ids)`` where each row follows :data:`FEATURE_NAMES`
        order.
    """
    demographics = demographics or {}
    rows: list[list[float]] = []
    ids: list[str] = []
    for tl in timelines:
        demo = demographics.get(tl.patient_id, {})
        feats = extract_features(tl, birth_year=demo.get("birth_year"))
        rows.append([feats[name] for name in FEATURE_NAMES])
        ids.append(tl.patient_id)
    return rows, ids


def describe_features() -> str:
    """Human-readable table of the feature set (for docs/reports)."""
    lines = ["feature | description", "--- | ---"]
    lines.extend(
        f"{name} | {FEATURE_DESCRIPTIONS[name]}" for name in FEATURE_NAMES
    )
    return "\n".join(lines)
