"""clinical — coding and phenotyping layer.

Maps raw ingested records to structured clinical concepts: ICD-10 (including
the L73.x hidradenitis family and common comorbidity codes), ICD-11 and SNOMED
CT crosswalks, versioned computable phenotypes, diagnostic-delay analytics,
and clinical instrument helpers.
"""

from sidha.clinical import codes, instruments, phenotypes
from sidha.clinical.codes import describe as describe_code
from sidha.clinical.codes import group_codes
from sidha.clinical.icd10 import (
    ALL_CODES,
    COMORBIDITIES,
    HS_FAMILY,
    RELATED_SKIN,
    describe,
    find_by_keyword,
    is_hs_code,
    normalize_code,
)
from sidha.clinical.instruments import hurley_stage, score_likert_scale
from sidha.clinical.phenotypes import (
    PHENOTYPE_VERSION,
    comorbidity_profile,
    diagnostic_delay_days,
    has_comorbidity,
    hs_case,
    summarize_cohort,
)

__all__ = [
    "ALL_CODES",
    "COMORBIDITIES",
    "HS_FAMILY",
    "RELATED_SKIN",
    "PHENOTYPE_VERSION",
    "codes",
    "describe",
    "describe_code",
    "diagnostic_delay_days",
    "comorbidity_profile",
    "find_by_keyword",
    "group_codes",
    "has_comorbidity",
    "hs_case",
    "hurley_stage",
    "instruments",
    "is_hs_code",
    "normalize_code",
    "phenotypes",
    "score_likert_scale",
    "summarize_cohort",
]
