"""datasets — public data loaders, catalog, and synthetic cohorts."""

from .catalog import catalog, with_loaders
from .synthetic import generate_cohort

__all__ = ["catalog", "generate_cohort", "with_loaders"]
