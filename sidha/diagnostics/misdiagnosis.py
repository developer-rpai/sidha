"""Cohort-level misdiagnosis-pattern reports.

Aggregates what coded diagnoses HS patients carry *before* their confirmed
HS diagnosis lands: which codes, how often, and how long the delay from each
code's first appearance to the HS diagnosis is. Complements
:func:`sidha.clinical.phenotypes.diagnostic_delay_days` (patient-level delay)
with the cohort-level picture researchers need for "what gets misdiagnosed
as what" analyses.

All outputs are aggregate counts and medians — no patient-level data.
"""

from __future__ import annotations

from statistics import median

from ..clinical import codes
from ..clinical.phenotypes import PHENOTYPE_VERSION, hs_case
from ..ehr.events import PatientTimeline

# Code groups that commonly precede an HS diagnosis (the misdiagnosis set).
MISDIAGNOSIS_GROUPS = ("abscess", "acne_vulgaris", "pilonidal", "hs_family")


def _median(values: list[float]) -> float | None:
    return round(median(values), 1) if values else None


def misdiagnosis_report(timelines: list[PatientTimeline]) -> dict:
    """Build the cohort misdiagnosis-pattern report.

    Only timelines meeting :func:`~sidha.clinical.phenotypes.hs_case` are
    included as cases; the rest are counted under ``n_excluded``.

    Returns a dict with:

    - ``n_cases`` / ``n_excluded``: case and non-case timeline counts.
    - ``phenotype_version``: the phenotype version used for case selection.
    - ``codes``: per ICD-10 code, ``patients`` (cases with the code before
      HS diagnosis), ``share`` (fraction of cases), and
      ``median_delay_days`` (first code occurrence -> HS diagnosis).
    - ``median_delay_days_overall``: median across cases of first
      misdiagnosis-coded date -> HS diagnosis.
    - ``common_first_codes``: most frequent first pre-diagnosis codes.
    """
    cases = [t for t in timelines if hs_case(t)]
    excluded = len(timelines) - len(cases)

    per_code: dict[str, dict] = {}
    first_code_counts: dict[str, int] = {}
    overall_delays: list[int] = []

    for tl in cases:
        hs_dates = [
            e.event_date
            for e in tl.of_type("condition")
            if e.code_system == "ICD10" and e.code in codes.group_codes("hs")
        ]
        if not hs_dates:
            continue
        dx_date = min(hs_dates)

        pre: list = []
        for group in MISDIAGNOSIS_GROUPS:
            wanted = codes.group_codes(group)
            pre.extend(
                e
                for e in tl.of_type("condition")
                if e.code_system == "ICD10"
                and e.code in wanted
                and e.code != "L73.2"
                and e.event_date < dx_date
            )
        if pre:
            first = min(pre, key=lambda e: e.event_date)
            first_code_counts[first.code] = first_code_counts.get(first.code, 0) + 1
            overall_delays.append((dx_date - first.event_date).days)

        seen: set[str] = set()
        for e in pre:
            if e.code in seen:
                continue
            seen.add(e.code)
            entry = per_code.setdefault(
                e.code, {"patients": 0, "delays": []}
            )
            entry["patients"] += 1
            first_for_code = min(
                x.event_date for x in pre if x.code == e.code
            )
            entry["delays"].append((dx_date - first_for_code).days)

    code_rows = {
        code: {
            "patients": entry["patients"],
            "share": round(entry["patients"] / len(cases), 3) if cases else 0.0,
            "median_delay_days": _median(entry["delays"]),
        }
        for code, entry in sorted(
            per_code.items(), key=lambda kv: kv[1]["patients"], reverse=True
        )
    }

    return {
        "phenotype_version": PHENOTYPE_VERSION,
        "n_cases": len(cases),
        "n_excluded": excluded,
        "codes": code_rows,
        "median_delay_days_overall": _median(overall_delays),
        "common_first_codes": dict(
            sorted(first_code_counts.items(), key=lambda kv: kv[1], reverse=True)
        ),
    }
