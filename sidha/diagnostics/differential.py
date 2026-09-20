"""Differential-diagnosis ranking with evidence reasons.

A deterministic, evidence-accumulating ranker over the conditions HS is most
often confused with. Each candidate accumulates supporting and refuting
evidence from the patient timeline; results are ranked by total evidence and
carry human-readable reasons so a researcher can see *why* a candidate ranks
where it does.

This is a research aid for studying misdiagnosis patterns, not a diagnostic
device. It complements the LLM-as-judge harness in :mod:`sidha.judge`:
use this module for transparent rule-based baselines, the judge harness for
LLM-based evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..clinical import codes
from ..ehr.events import PatientTimeline


@dataclass
class DifferentialCandidate:
    """One ranked differential candidate with its evidence trail."""

    name: str
    code: str
    code_system: str
    score: float
    supporting: list[str] = field(default_factory=list)
    refuting: list[str] = field(default_factory=list)


def _count(timeline: PatientTimeline, group: str) -> int:
    wanted = codes.group_codes(group)
    return sum(
        1
        for e in timeline.of_type("condition")
        if e.code_system == "ICD10" and e.code in wanted
    )


def _distinct_dates(timeline: PatientTimeline, group: str) -> int:
    wanted = codes.group_codes(group)
    return len(
        {
            e.event_date
            for e in timeline.of_type("condition")
            if e.code_system == "ICD10" and e.code in wanted
        }
    )


def rank_differentials(timeline: PatientTimeline) -> list[DifferentialCandidate]:
    """Rank HS and its common mimics by accumulated evidence.

    Candidates: hidradenitis suppurativa, cutaneous abscess/furuncle, acne
    vulgaris, pilonidal disease, cellulitis, and fistulizing Crohn's disease.
    Returns candidates sorted by descending score; ties break alphabetically
    for determinism.
    """
    abscess_n = _count(timeline, "abscess")
    acne_n = _count(timeline, "acne_vulgaris")
    pilonidal_n = _count(timeline, "pilonidal")
    hs_n = _count(timeline, "hs")
    other_hs_family_n = sum(
        1
        for e in timeline.of_type("condition")
        if e.code_system == "ICD10"
        and e.code in codes.group_codes("hs_family")
        and e.code != "L73.2"
    )
    crohn_n = _count(timeline, "crohn")
    conditions = timeline.of_type("condition")
    span_years = (
        (max(e.event_date for e in conditions)
         - min(e.event_date for e in conditions)).days / 365.25
        if len(conditions) > 1
        else 0.0
    )
    distinct_abscess_dates = _distinct_dates(timeline, "abscess")

    cands: list[DifferentialCandidate] = []

    # --- Hidradenitis suppurativa ---
    hs = DifferentialCandidate("Hidradenitis suppurativa", "L73.2", "ICD10", 0.0)
    if hs_n:
        hs.supporting.append(f"confirmed HS code present ({hs_n} event(s))")
        hs.score += 5.0
    if distinct_abscess_dates >= 3:
        hs.supporting.append(
            f"recurrent abscess/furuncle coding on {distinct_abscess_dates} dates"
        )
        hs.score += 2.0
    if pilonidal_n:
        hs.supporting.append("pilonidal disease co-coded (shared follicular-occlusion pattern)")
        hs.score += 1.0
    if acne_n >= 2:
        hs.supporting.append("persistent acne vulgaris coding")
        hs.score += 0.75
    if other_hs_family_n:
        hs.supporting.append("other L73-family codes present")
        hs.score += 0.75
    if span_years >= 2:
        hs.supporting.append(f"multi-year coded course ({span_years:.1f} years)")
        hs.score += 1.0
    if not hs.supporting:
        hs.refuting.append("no HS-suggestive codes in timeline")
    cands.append(hs)

    # --- Cutaneous abscess / furuncle ---
    ab = DifferentialCandidate("Cutaneous abscess / furuncle", "L02.9", "ICD10", 0.0)
    if abscess_n:
        ab.supporting.append(f"abscess/furuncle coded ({abscess_n} event(s))")
        ab.score += 2.0
    if distinct_abscess_dates == 1:
        ab.supporting.append("single-episode pattern")
        ab.score += 0.5
    if distinct_abscess_dates >= 3:
        ab.refuting.append("recurrence across multiple dates favors chronic disease")
        ab.score -= 1.0
    if pilonidal_n or acne_n >= 2:
        ab.refuting.append("co-coded pilonidal/acne pattern is atypical for simple abscess")
        ab.score -= 0.5
    if not abscess_n:
        ab.refuting.append("no abscess codes in timeline")
    cands.append(ab)

    # --- Acne vulgaris ---
    ac = DifferentialCandidate("Acne vulgaris", "L70.0", "ICD10", 0.0)
    if acne_n:
        ac.supporting.append(f"acne vulgaris coded ({acne_n} event(s))")
        ac.score += 2.0
    if abscess_n >= 2:
        ac.refuting.append("recurrent abscess coding is atypical for acne alone")
        ac.score -= 1.0
    if pilonidal_n:
        ac.refuting.append("pilonidal co-coding points away from acne alone")
        ac.score -= 0.5
    if not acne_n:
        ac.refuting.append("no acne codes in timeline")
    cands.append(ac)

    # --- Pilonidal disease ---
    pi = DifferentialCandidate("Pilonidal disease", "L05.91", "ICD10", 0.0)
    if pilonidal_n:
        pi.supporting.append(f"pilonidal disease coded ({pilonidal_n} event(s))")
        pi.score += 2.0
    if abscess_n >= 3 and not pilonidal_n:
        pi.refuting.append("widespread abscess coding without pilonidal codes")
        pi.score -= 0.5
    if not pilonidal_n:
        pi.refuting.append("no pilonidal codes in timeline")
    cands.append(pi)

    # --- Cellulitis ---
    ce = DifferentialCandidate("Cellulitis", "L03.9", "ICD10", 0.0)
    if distinct_abscess_dates == 1 and span_years < 1:
        ce.supporting.append("single acute skin-infection episode")
        ce.score += 1.0
    if distinct_abscess_dates >= 2:
        ce.refuting.append("recurrence is atypical for cellulitis")
        ce.score -= 1.0
    if span_years >= 2:
        ce.refuting.append("multi-year course is atypical for cellulitis")
        ce.score -= 0.5
    cands.append(ce)

    # --- Fistulizing Crohn's disease ---
    cr = DifferentialCandidate(
        "Fistulizing Crohn's disease", "K50.90", "ICD10", 0.0
    )
    if crohn_n:
        cr.supporting.append("Crohn's disease coded — consider cutaneous/fistulizing involvement")
        cr.score += 2.0
    if crohn_n and abscess_n >= 2:
        cr.supporting.append("recurrent abscesses in a Crohn's patient")
        cr.score += 1.0
    if not crohn_n:
        cr.refuting.append("no inflammatory bowel disease codes in timeline")
    cands.append(cr)

    cands.sort(key=lambda c: (-c.score, c.name))
    return cands
