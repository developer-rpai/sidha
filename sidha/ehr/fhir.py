"""FHIR R4 Bundle loader.

Reads a FHIR R4 ``Bundle`` (JSON) of clinical resources and converts the
supported resource types into :class:`ClinicalEvent` objects:

- Condition -> condition
- MedicationStatement / MedicationRequest -> medication
- Procedure -> procedure
- Observation -> observation
- Encounter -> encounter

Only the first coding of each resource's primary ``code`` element is used.
Resources without a usable patient reference, date, or code are skipped and
counted in the returned report.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .events import ClinicalEvent

_RESOURCE_TO_TYPE = {
    "Condition": "condition",
    "MedicationStatement": "medication",
    "MedicationRequest": "medication",
    "Procedure": "procedure",
    "Observation": "observation",
    "Encounter": "encounter",
}

# Date fields tried in order for each resource type.
_DATE_FIELDS = {
    "Condition": ("onsetDateTime", "recordedDate"),
    "MedicationStatement": ("effectiveDateTime", "dateAsserted"),
    "MedicationRequest": ("authoredOn",),
    "Procedure": ("performedDateTime", "performedPeriod"),
    "Observation": ("effectiveDateTime", "issued"),
    "Encounter": ("period",),
}


def _patient_id(resource: dict[str, Any]) -> str | None:
    ref = (resource.get("subject") or {}).get("reference") or ""
    # "Patient/abc-123" -> "abc-123"
    return ref.split("/", 1)[1] if "/" in ref else (ref or None)


def _event_date(resource: dict[str, Any]) -> date | None:
    for field_name in _DATE_FIELDS.get(resource.get("resourceType", ""), ()):
        raw = resource.get(field_name)
        if isinstance(raw, dict):  # Period-like: use start
            raw = raw.get("start")
        if isinstance(raw, str) and len(raw) >= 10:
            try:
                return date.fromisoformat(raw[:10])
            except ValueError:
                continue
    return None


def _code(resource: dict[str, Any]) -> tuple[str, str, str] | None:
    coding = (resource.get("code") or {}).get("coding") or []
    if not coding:
        return None
    first = coding[0]
    code = str(first.get("code", "")).strip()
    if not code:
        return None
    system = str(first.get("system", "")).strip().upper()
    display = str(first.get("display", "")).strip()
    return code, system or "UNKNOWN", display


def _value(resource: dict[str, Any]) -> str:
    if resource.get("resourceType") != "Observation":
        return ""
    vq = resource.get("valueQuantity") or {}
    if "value" in vq:
        return f"{vq['value']} {vq.get('unit', '')}".strip()
    for key in ("valueString", "valueCodeableConcept"):
        if key in resource:
            val = resource[key]
            if isinstance(val, dict):
                return val.get("text", "")
            return str(val)
    return ""


def load_bundle(path: str | Path) -> tuple[list[ClinicalEvent], dict[str, int]]:
    """Load a FHIR R4 Bundle JSON file into clinical events.

    Returns ``(events, report)`` where report counts loaded, skipped, and
    unsupported resources.
    """
    bundle = json.loads(Path(path).read_text(encoding="utf-8"))
    events: list[ClinicalEvent] = []
    report = {"loaded": 0, "skipped": 0, "unsupported": 0}
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        rtype = resource.get("resourceType", "")
        event_type = _RESOURCE_TO_TYPE.get(rtype)
        if event_type is None:
            report["unsupported"] += 1
            continue
        pid = _patient_id(resource)
        edate = _event_date(resource)
        coded = _code(resource)
        if pid is None or edate is None or coded is None:
            report["skipped"] += 1
            continue
        code, system, display = coded
        events.append(
            ClinicalEvent(
                patient_id=pid,
                event_date=edate,
                event_type=event_type,
                code=code,
                code_system=system,
                display=display,
                value=_value(resource),
            )
        )
        report["loaded"] += 1
    return events, report
