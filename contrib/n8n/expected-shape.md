# Expected fixture shape

Minimal note for a future n8n check. Not a workflow result. No numeric
thresholds.

The fields below are what `sidha.ehr` reads. They are not the full OMOP
CDM mandatory column set and not an HL7 profile. Hidradenitis suppurativa
is the flagship example in some sample codes. The columns themselves are
not HS-specific.

Source of the lists: `sidha/ehr/csv_loader.py`, `sidha/ehr/omop.py`, and
`sidha/ehr/fhir.py` on `main` at
`7d73ee824910969f27ea9c545de9200e7794bebd`.

## Flat CSV (`load_csv`)

Documented header:

`patient_id,event_date,event_type,code,code_system,display,value`

Required (`REQUIRED_COLUMNS`): `patient_id`, `event_date`, `event_type`,
`code`, `code_system`. `display` and `value` are optional.

`event_type` must be one of `condition`, `medication`, `procedure`,
`observation`, `encounter`. `event_date` is `YYYY-MM-DD`.

Committed file: `data/synthetic/ehr_sample.csv`.

## OMOP CDM CSV (`load_omop`)

Columns the loader reads. Missing tables are skipped. A row is not loaded
when the date does not parse, or the concept id is empty or `0`.

| File | Columns read |
| --- | --- |
| `CONDITION_OCCURRENCE.csv` | `person_id`, `condition_concept_id`, `condition_start_date`, `condition_source_value` |
| `DRUG_EXPOSURE.csv` | `person_id`, `drug_concept_id`, `drug_exposure_start_date`, `drug_source_value` |
| `PROCEDURE_OCCURRENCE.csv` | `person_id`, `procedure_concept_id`, `procedure_date`, `procedure_source_value` |
| `OBSERVATION.csv` | `person_id`, `observation_concept_id`, `observation_date`, `observation_source_value` |
| `MEASUREMENT.csv` | `person_id`, `measurement_concept_id`, `measurement_date`, `measurement_source_value` |

The sample directory commits only `CONDITION_OCCURRENCE.csv` and
`DRUG_EXPOSURE.csv`.

## FHIR R4 Bundle (`load_bundle`)

`data/synthetic/fhir_bundle_sample.json` has root `resourceType` `Bundle`
and `type` `collection`.

Allowed `entry[].resource.resourceType` values:

`Condition`, `MedicationStatement`, `MedicationRequest`, `Procedure`,
`Observation`, `Encounter`.

For each resource the loader looks for `subject.reference`,
`code.coding[0].code`, and a date:

| resourceType | Date fields, in order |
| --- | --- |
| Condition | `onsetDateTime`, `recordedDate` |
| MedicationStatement | `effectiveDateTime`, `dateAsserted` |
| MedicationRequest | `authoredOn` |
| Procedure | `performedDateTime`, `performedPeriod` (`start`) |
| Observation | `effectiveDateTime`, `issued` |
| Encounter | `period` (`start`) |

If patient, code, or date is missing, the resource is counted as
`skipped`. That is not a crash. Other resource types are `unsupported`.

The committed bundle includes one Condition with a subject and a code
and no `onsetDateTime` or `recordedDate`: ICD-10 E66.9. The L73.2
Condition in the same file does have `onsetDateTime`. This note does not
quote a `skipped` integer from a fresh `load_bundle` call.
