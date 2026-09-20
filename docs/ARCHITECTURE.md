# SIDHA Architecture

**Sensor-to-Insight Data for Hidradenitis Suppurativa Architecture** — a layered
reference design for converting episodic, heterogeneous HS data into continuous,
standards-based, research-ready intelligence.

## Design principles

1. **Standards-based output.** Everything analytically useful exits the pipeline
   as OMOP CDM tables or FHIR R4 resources. No proprietary intermediate formats
   that only one lab can read.
2. **Patient language is first-class input.** People describe HS in everyday
   words ("boils that keep coming back in the armpit"). The taxonomy layer maps
   that language to clinical concepts (ICD-10, SNOMED CT) instead of discarding it.
3. **Public data only, by construction.** Social-listening ingestors read public
   discussions and honor platform terms/robots.txt. No PHI ever enters the repo;
   `data/` holds synthetic or sample data only.
4. **Evaluation is part of the architecture.** The LLM-as-judge harness ships
   with the framework so analytic claims (e.g., differential-diagnosis ranking)
   are reproducible against synthetic golden sets.

## Layers

### 1. `ingest` — capture
Collectors for public social-listening sources (Reddit, X, HS-related Facebook
groups) plus loaders for episodic clinical/diagnostic record exports. Each
collector records provenance (source, retrieval timestamp, query) alongside the
raw payload.

### 2. `clinical` — code
Maps raw records to structured clinical concepts: ICD-10 (including the L73.x
hidradenitis family and common comorbidity codes), procedure/drug vocabularies,
and diagnostic timelines. Produces code-annotated case records.

### 3. `taxonomy` — translate (the novel piece)
Patient-language → clinical-taxonomy mapper. Learns/encodes the mapping from
colloquial symptom descriptions to controlled vocabularies, so "recurring
painful lumps" and "L73.2" become the same analytic object. This is the layer
most existing pipelines skip — and the one this framework exists to provide.

### 4. `normalize` — standardize
Converts taxonomy-mapped records into OMOP CDM tables and FHIR R4 resources
(Condition, Observation, MedicationStatement, etc.), ready for OHDSI tooling
(ATLAS, DataQualityDashboard) and FHIR analytics (e.g., Pathling).

### 5. `judge` — assess
LLM-as-judge harness for differential-diagnosis evaluation: given a case
vignette and candidate diagnoses, an LLM judge scores ranking quality.
Prompt templates, judge rubrics, and scoring logic live here — swappable
across models.

### 6. `eval` — measure
Metrics plus synthetic golden test sets. Golden cases are hand-constructed
vignettes with known-correct rankings; they are synthetic by design so the
repo never touches real patient data.

## Data flow

```
public discussions ─┐
                    ├─▶ ingest ─▶ clinical ─▶ taxonomy ─▶ normalize ─▶ OMOP / FHIR
episodic records ───┘                                                      │
                                                                           ▼
                                                     judge ◀── case vignettes
                                                       │
                                                       ▼
                                                  eval (metrics)
```

## Non-goals

- Not a diagnostic device or clinical decision support tool.
- Not a data warehouse — it produces standards-based artifacts; storage is the
  consumer's choice.
- Not a scraper that ignores platform terms. Collectors must honor robots.txt
  and API terms of service.
