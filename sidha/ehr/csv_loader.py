"""Flat CSV loader for clinical records.

Expected columns (header row required):

    patient_id, event_date, event_type, code, code_system, display, value

- ``event_date``: ISO date (YYYY-MM-DD).
- ``event_type``: condition | medication | procedure | observation | encounter.
- ``display`` and ``value`` are optional.

This is the simplest on-ramp for researchers: export whatever you have to this
shape and the rest of SIDHA works unchanged.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .events import ClinicalEvent

REQUIRED_COLUMNS = (
    "patient_id",
    "event_date",
    "event_type",
    "code",
    "code_system",
)

VALID_EVENT_TYPES = {"condition", "medication", "procedure", "observation", "encounter"}


def load_csv(path: str | Path) -> list[ClinicalEvent]:
    """Load clinical events from a CSV file in the documented schema."""
    path = Path(path)
    events: list[ClinicalEvent] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")
        for lineno, row in enumerate(reader, start=2):
            event_type = row["event_type"].strip().lower()
            if event_type not in VALID_EVENT_TYPES:
                raise ValueError(
                    f"line {lineno}: unknown event_type {row['event_type']!r}"
                )
            try:
                event_date = date.fromisoformat(row["event_date"].strip())
            except ValueError as exc:
                raise ValueError(
                    f"line {lineno}: bad event_date {row['event_date']!r}"
                ) from exc
            events.append(
                ClinicalEvent(
                    patient_id=row["patient_id"].strip(),
                    event_date=event_date,
                    event_type=event_type,
                    code=row["code"].strip(),
                    code_system=row["code_system"].strip().upper(),
                    display=(row.get("display") or "").strip(),
                    value=(row.get("value") or "").strip(),
                )
            )
    return events


def write_csv(events: list[ClinicalEvent], path: str | Path) -> None:
    """Write clinical events back out in the documented CSV schema."""
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["patient_id", "event_date", "event_type", "code", "code_system", "display", "value"]
        )
        for e in events:
            writer.writerow(
                [
                    e.patient_id,
                    e.event_date.isoformat(),
                    e.event_type,
                    e.code,
                    e.code_system,
                    e.display,
                    e.value,
                ]
            )
