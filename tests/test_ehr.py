"""Tests for the EHR ingestion layer: events, CSV, FHIR, and OMOP loaders."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from sidha.ehr import (
    ClinicalEvent,
    PatientTimeline,
    build_timelines,
    load_bundle,
    load_csv,
    load_omop,
    write_csv,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"


def test_timeline_orders_events():
    t = PatientTimeline("P1")
    t.add(ClinicalEvent("P1", date(2023, 1, 20), "condition", "L73.2", "ICD10"))
    t.add(ClinicalEvent("P1", date(2019, 3, 14), "condition", "L02.9", "ICD10"))
    assert [e.code for e in t.events] == ["L02.9", "L73.2"]
    assert t.first_date("L73.2") == date(2023, 1, 20)


def test_timeline_rejects_other_patient():
    t = PatientTimeline("P1")
    with pytest.raises(ValueError):
        t.add(ClinicalEvent("P2", date(2023, 1, 1), "condition", "L73.2", "ICD10"))


def test_build_timelines_groups_by_patient():
    events = [
        ClinicalEvent("P1", date(2023, 1, 1), "condition", "L73.2", "ICD10"),
        ClinicalEvent("P2", date(2023, 2, 1), "condition", "L73.2", "ICD10"),
    ]
    timelines = build_timelines(events)
    assert set(timelines) == {"P1", "P2"}
    assert len(timelines["P1"]) == 1


def test_csv_loader_round_trip(tmp_path):
    events = load_csv(DATA / "ehr_sample.csv")
    assert len(events) == 9
    assert {e.patient_id for e in events} == {"P001", "P002", "P003"}
    out = tmp_path / "out.csv"
    write_csv(events, out)
    assert load_csv(out) == events


def test_csv_loader_rejects_bad_schema(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("patient_id,event_date\nP1,2023-01-01\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_csv(bad)


def test_csv_loader_rejects_bad_type(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "patient_id,event_date,event_type,code,code_system\n"
        "P1,2023-01-01,surgery,X,ICD10\n"
    )
    with pytest.raises(ValueError, match="unknown event_type"):
        load_csv(bad)


def test_fhir_bundle_loader():
    events, report = load_bundle(DATA / "fhir_bundle_sample.json")
    # 5 entries: 4 loadable, 1 skipped (no date), 0 unsupported
    assert report == {"loaded": 4, "skipped": 1, "unsupported": 0}
    by_patient = build_timelines(events)
    assert by_patient["P001"].first_date("L73.2") == date(2023, 1, 20)
    meds = by_patient["P001"].of_type("medication")
    assert len(meds) == 1 and meds[0].code_system == "HTTP://WWW.NLM.NIH.GOV/RESEARCH/UMLS/RXNORM"


def test_omop_loader():
    events, report = load_omop(DATA / "omop_sample")
    assert report == {"CONDITION_OCCURRENCE": 3, "DRUG_EXPOSURE": 1}
    assert all(e.code_system == "OMOP" for e in events)
    by_patient = build_timelines(events)
    assert by_patient["P001"].first_date("137810") == date(2023, 1, 20)
    assert by_patient["P001"].of_type("medication")[0].display == "adalimumab"
