"""Catalog of known hidradenitis suppurativa data sources.

HS-specific open datasets are scarce. This catalog gives researchers one
place to see what exists, how to access it, and whether SIDHA ships a
loader for it yet. ``loader`` is one of: "available", "planned", "gated"
(requires an access request), or "none".
"""

from __future__ import annotations

SOURCES: list[dict[str, str]] = [
    {
        "name": "GEO HS transcriptomic datasets",
        "modality": "genomics",
        "access": "public",
        "loader": "planned",
        "notes": "Bulk and single-cell RNA-seq HS studies deposited in NCBI GEO; "
        "loader will wrap GEOparse.",
    },
    {
        "name": "Legit.Health-HS-IHS4",
        "modality": "imaging",
        "access": "public",
        "loader": "planned",
        "notes": "221 HS lesion images annotated for IHS4 severity by six "
        "dermatologists; loader pending license confirmation.",
    },
    {
        "name": "SIDHA synthetic cohort",
        "modality": "ehr",
        "access": "public",
        "loader": "available",
        "notes": "Built-in generator (sidha.datasets.synthetic); no PHI, "
        "runs every tutorial and test.",
    },
    {
        "name": "HS PROGRESS registry",
        "modality": "registry",
        "access": "gated",
        "loader": "none",
        "notes": "Prospective HS registry; contact the registry for access.",
    },
    {
        "name": "TARGET-DERM HS cohort",
        "modality": "registry",
        "access": "gated",
        "loader": "none",
        "notes": "Longitudinal dermatology registry with an HS cohort; "
        "data-use agreement required.",
    },
    {
        "name": "OM1 HS dataset",
        "modality": "ehr",
        "access": "commercial",
        "loader": "none",
        "notes": "~26k HS patient records with ML-derived Hurley staging; "
        "commercial license.",
    },
    {
        "name": "StuffThatWorks HS community PROs",
        "modality": "patient-reported",
        "access": "gated",
        "loader": "none",
        "notes": "1,050-patient HS cohort with treatment-effectiveness "
        "ratings; research collaboration required.",
    },
]


def catalog() -> list[dict[str, str]]:
    """Return the dataset catalog as a list of dicts."""
    return [dict(s) for s in SOURCES]


def with_loaders() -> list[dict[str, str]]:
    """Return only sources SIDHA can load today."""
    return [s for s in catalog() if s["loader"] == "available"]
