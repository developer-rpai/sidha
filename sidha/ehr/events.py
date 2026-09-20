"""Core event model for SIDHA's EHR layer.

Everything the EHR loaders produce converges on one simple type,
``ClinicalEvent``: one coded thing that happened to one patient on one date.
``PatientTimeline`` collects a patient's events in chronological order and
provides the queries the clinical modules need.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class ClinicalEvent:
    """One coded clinical event for one patient on one date."""

    patient_id: str
    event_date: date
    event_type: str  # condition | medication | procedure | observation | encounter
    code: str
    code_system: str  # e.g. ICD10, ICD11, SNOMED, OMOP, RXNORM, LOINC
    display: str = ""
    value: str = ""


@dataclass
class PatientTimeline:
    """Chronological event history for a single patient."""

    patient_id: str
    events: list[ClinicalEvent] = field(default_factory=list)

    def add(self, event: ClinicalEvent) -> None:
        if event.patient_id != self.patient_id:
            raise ValueError("event belongs to a different patient")
        self.events.append(event)
        self.events.sort(key=lambda e: e.event_date)

    def of_type(self, event_type: str) -> list[ClinicalEvent]:
        return [e for e in self.events if e.event_type == event_type]

    def with_code(self, code: str) -> list[ClinicalEvent]:
        return [e for e in self.events if e.code == code]

    def first_date(self, code: str) -> date | None:
        dates = [e.event_date for e in self.with_code(code)]
        return min(dates) if dates else None

    def between(self, start: date, end: date) -> list[ClinicalEvent]:
        return [e for e in self.events if start <= e.event_date <= end]

    def __len__(self) -> int:
        return len(self.events)


def build_timelines(events: list[ClinicalEvent]) -> dict[str, PatientTimeline]:
    """Group a flat event list into one timeline per patient."""
    timelines: dict[str, PatientTimeline] = {}
    for event in events:
        timelines.setdefault(event.patient_id, PatientTimeline(event.patient_id)).add(event)
    return timelines
