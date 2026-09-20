"""SIDHA — Sensor-to-Insight Data for Hidradenitis Suppurativa Architecture.

Open reference implementation: ingest heterogeneous HS data, map patient
language to clinical taxonomies, normalize to OMOP CDM / FHIR R4, and evaluate
analytic approaches with an LLM-as-judge harness.
"""

__version__ = "0.1.0"
__all__ = [
    "ingest",
    "ehr",
    "clinical",
    "diagnostics",
    "datasets",
    "taxonomy",
    "normalize",
    "judge",
    "eval",
]
