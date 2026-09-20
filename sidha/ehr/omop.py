"""OMOP CDM extract loader.

Reads a directory of OMOP CDM v5.x table extracts as CSV files and converts
the supported tables into :class:`ClinicalEvent` objects:

- CONDITION_OCCURRENCE -> condition (condition_concept_id, condition_start_date)
- DRUG_EXPOSURE -> medication (drug_concept_id, drug_exposure_start_date)
- PROCEDURE_OCCURRENCE -> procedure (procedure_concept_id, procedure_date)
- OBSERVATION -> observation (observation_concept_id, observation_date)
- MEASUREMENT -> observation (measurement_concept_id, measurement_date)

Concept IDs are kept as codes with ``code_system="OMOP"``; the source value
columns (e.g. condition_source_value) are preserved in the display field when
present. Tables that are missing are simply skipped.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .events import ClinicalEvent

# table file -> (event_type, person_id_col, concept_id_col, date_col, source_value_col)
_TABLES: dict[str, tuple[str, str, str, str, str]] = {
    "CONDITION_OCCURRENCE": (
        "condition",
        "person_id",
        "condition_concept_id",
        "condition_start_date",
        "condition_source_value",
    ),
    "DRUG_EXPOSURE": (
        "medication",
        "person_id",
        "drug_concept_id",
        "drug_exposure_start_date",
        "drug_source_value",
    ),
    "PROCEDURE_OCCURRENCE": (
        "procedure",
        "person_id",
        "procedure_concept_id",
        "procedure_date",
        "procedure_source_value",
    ),
    "OBSERVATION": (
        "observation",
        "person_id",
        "observation_concept_id",
        "observation_date",
        "observation_source_value",
    ),
    "MEASUREMENT": (
        "observation",
        "person_id",
        "measurement_concept_id",
        "measurement_date",
        "measurement_source_value",
    ),
}


def _parse_date(raw: str) -> date | None:
    raw = (raw or "").strip()
    if len(raw) < 10:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def load_omop(directory: str | Path) -> tuple[list[ClinicalEvent], dict[str, int]]:
    """Load OMOP CDM table CSVs from a directory into clinical events.

    Returns ``(events, report)`` where report maps each table name found to
    the number of events loaded from it.
    """
    directory = Path(directory)
    events: list[ClinicalEvent] = []
    report: dict[str, int] = {}
    for table, (event_type, pid_col, concept_col, date_col, src_col) in _TABLES.items():
        path = directory / f"{table}.csv"
        if not path.exists():
            continue
        count = 0
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                edate = _parse_date(row.get(date_col, ""))
                concept_id = (row.get(concept_col) or "").strip()
                if edate is None or not concept_id or concept_id == "0":
                    continue
                events.append(
                    ClinicalEvent(
                        patient_id=(row.get(pid_col) or "").strip(),
                        event_date=edate,
                        event_type=event_type,
                        code=concept_id,
                        code_system="OMOP",
                        display=(row.get(src_col) or "").strip(),
                    )
                )
                count += 1
        report[table] = count
    return events, report
