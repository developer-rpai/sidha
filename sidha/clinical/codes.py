"""Cross-system code mappings for HS and its common comorbidities.

Covers ICD-10-CM (see :mod:`sidha.clinical.icd10` for the full table), ICD-11
MMS, and SNOMED CT. Every entry here is a *reference* mapping: verify against
the current WHO ICD-11 release and the current SNOMED CT release before any
clinical, billing, or registry use. **Not medical advice.**
"""

from __future__ import annotations

from .icd10 import normalize_code as normalize_icd10

# ICD-11 MMS codes. HS sits in chapter 24 (disorders of the skin).
# Provisional: confirm against the current WHO ICD-11 browser.
ICD11: dict[str, str] = {
    "ED92.0": "Hidradenitis suppurativa",
    "5A11": "Type 2 diabetes mellitus",
    "5B81": "Obesity",
    "6A70": "Depressive disorders",
    "6B00": "Generalised anxiety disorder",
    "DA90": "Crohn disease",
    "5A80.1": "Polycystic ovary syndrome",
}

# SNOMED CT concept IDs. Provisional: validate against the current SNOMED CT
# release; IDs are included so pipelines have a starting crosswalk to refine.
SNOMED: dict[str, str] = {
    "3723001": "Hidradenitis suppurativa",
    "44054006": "Diabetes mellitus type 2",
    "414915002": "Obesity",
    "35489007": "Depressive disorder",
    "48694002": "Anxiety disorder",
    "34000006": "Crohn's disease",
    "237055002": "Polycystic ovary syndrome",
}

# Condition groups used by the phenotyping module: each maps a canonical
# condition name to the ICD-10-CM codes that identify it in EHR data.
CONDITION_GROUPS: dict[str, set[str]] = {
    "hs": {"L73.2"},
    "hs_family": {"L73.0", "L73.1", "L73.2", "L73.8", "L73.9"},
    "abscess": {"L02.9"},
    "acne_vulgaris": {"L70.0"},
    "pilonidal": {"L05.91", "L05.92"},
    "obesity": {"E66.9", "E66.01", "E66.09"},
    "diabetes_t2": {"E11.9", "E11.65"},
    "metabolic_syndrome": {"E88.81"},
    "depression": {"F32.9", "F32.0", "F32.1", "F33.9"},
    "anxiety": {"F41.1", "F41.9"},
    "nicotine": {"F17.210", "Z87.891"},
    "crohn": {"K50.90", "K50.00"},
    "ankylosing_spondylitis": {"M45.9"},
    "pcos": {"E28.2"},
}


def normalize_icd11(code: str) -> str:
    """Normalize an ICD-11 code: uppercase, strip whitespace."""
    return code.strip().upper()


def describe(code: str, system: str = "ICD10") -> str | None:
    """Describe a code in the given system (ICD10, ICD11, or SNOMED)."""
    system = system.strip().upper()
    if system == "ICD10":
        from .icd10 import describe as describe_icd10

        return describe_icd10(code)
    if system == "ICD11":
        return ICD11.get(normalize_icd11(code))
    if system == "SNOMED":
        return SNOMED.get(code.strip())
    raise ValueError(f"unknown code system: {system!r}")


def group_codes(group: str) -> set[str]:
    """Return the ICD-10-CM code set for a canonical condition group."""
    try:
        return set(CONDITION_GROUPS[group])
    except KeyError as exc:
        raise ValueError(f"unknown condition group: {group!r}") from exc
