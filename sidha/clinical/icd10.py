"""ICD-10-CM reference mapping for hidradenitis suppurativa and related codes.

This is a *reference* table for the SIDHA clinical-coding layer. Descriptions
follow ICD-10-CM conventions; verify against the current CMS release before
any clinical or billing use. **Not medical advice.**
"""

from __future__ import annotations

# Core HS family — L73: other follicular disorders
HS_FAMILY: dict[str, str] = {
    "L73.0": "Acne keloid",
    "L73.1": "Pseudofolliculitis barbae",
    "L73.2": "Hidradenitis suppurativa",
    "L73.8": "Other specified follicular disorders",
    "L73.9": "Follicular disorder, unspecified",
}

# Closely related / differential skin conditions
RELATED_SKIN: dict[str, str] = {
    "L02.9": "Cutaneous abscess, furuncle and carbuncle, unspecified",
    "L05.91": "Pilonidal cyst without abscess",
    "L05.92": "Pilonidal cyst with abscess",
    "L70.0": "Acne vulgaris",
    "L72.0": "Epidermal cyst",
}

# Conditions frequently comorbid with HS in the published literature
COMORBIDITIES: dict[str, str] = {
    "E66.9": "Obesity, unspecified",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "E88.81": "Metabolic syndrome",
    "F32.9": "Major depressive disorder, single episode, unspecified",
    "F41.1": "Generalized anxiety disorder",
    "F17.210": "Nicotine dependence, cigarettes, uncomplicated",
    "Z87.891": "Personal history of nicotine dependence",
    "K50.90": "Crohn's disease, unspecified, without complications",
    "M45.9": "Ankylosing spondylitis of unspecified sites in spine",
}

ALL_CODES: dict[str, str] = {**HS_FAMILY, **RELATED_SKIN, **COMORBIDITIES}


def normalize_code(code: str) -> str:
    """Normalize an ICD-10 code: uppercase, strip whitespace, canonical dot placement."""
    compact = code.strip().upper().replace(".", "")
    if len(compact) > 3:
        return compact[:3] + "." + compact[3:]
    return compact


def describe(code: str) -> str | None:
    """Return the description for an ICD-10 code, or None if not in the table."""
    return ALL_CODES.get(normalize_code(code))


def is_hs_code(code: str) -> bool:
    """True if the code belongs to the HS (L73) family."""
    return normalize_code(code) in HS_FAMILY


def find_by_keyword(keyword: str) -> list[tuple[str, str]]:
    """Case-insensitive keyword search over code descriptions."""
    needle = keyword.strip().lower()
    return [(c, d) for c, d in ALL_CODES.items() if needle in d.lower()]
