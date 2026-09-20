# SIDHA Big Package Plan — from scaffold to `pip install sidha`

Goal: turn the SIDHA scaffold into a robust, researcher-ready Python package that
other research groups can install, run, and extend. One package, many
functionalities: EHR ingestion, clinical coding and phenotyping, diagnostic
support, sensor streams, public dataset loaders, normalization to open standards,
and reproducible evaluation.

## Where things stand today

- The scaffold lives **only on this machine** at `~/workspace/profile-building/sidha`.
  Nothing has been pushed to GitHub yet. The GitHub repo creation and first push
  are still your tap (exact commands are in Phase 0 below).
- Current modules: `ingest` (Reddit collector), `clinical` (ICD-10 mapping),
  `taxonomy`, `normalize`, `judge`, `eval` (skeleton), synthetic fixtures, 11
  passing tests, CI workflow, Apache 2.0 license, CITATION.cff.
- This plan grows that scaffold into the full package described below. Nothing
  here replaces the existing 90-day roadmap; it extends it.

## Package architecture (target v1.0)

```
sidha/
  ehr/          EHR ingestion: FHIR R4 bundles, OMOP CDM extracts, CSV loaders,
                C-CDA hooks; connection helpers for common exports
  clinical/     ICD-10/ICD-11/SNOMED CT crosswalks; comorbidity phenotyping
                (depression, anxiety, PCOS, obesity, IBD, metabolic syndrome);
                Hurley staging helpers; HiSQOL / HSSD instrument scoring
  diagnostics/  diagnostic-delay analytics (first symptom code -> HS diagnosis);
                early-detection screener from claims/EHR patterns;
                differential-diagnosis ranking; misdiagnosis-pattern reports
  sensors/      wearable and sensor stream loaders; flare-event labeling;
                time-series feature extraction (sleep, activity, skin signals)
  datasets/     public dataset loaders + synthetic cohort generator (see below)
  nlp/          patient-language -> clinical taxonomy mapper; clinical-note
                section parsing; comorbidity and treatment extraction
  normalize/    OMOP CDM builders (Condition_Occurrence, Observation,
                Drug_Exposure, Measurement) and FHIR R4 builders
                (Condition, Observation, MedicationStatement)
  eval/         golden test sets, ranking metrics (top-k, MRR), reproducibility
                harness
  judge/        LLM-as-judge differential-diagnosis evaluation harness
  viz/          patient-journey timelines, comorbidity networks, flare charts,
                diagnostic-delay distributions
  privacy/      de-identification helpers, Safe Harbor guidance, k-anonymity
                checks for shared extracts
```

## Data coverage: what the package will handle

### 1. EHR data (`sidha.ehr`)
- Loaders for FHIR R4 Bundle JSON, OMOP CDM table extracts (CSV/Parquet), and
  flat clinical-record CSVs with a documented schema.
- Patient-journey builder: longitudinal record -> ordered event timeline per
  patient (encounters, conditions, meds, procedures).
- All loaders are format-first and PHI-agnostic: they document expected columns
  and validate input, and every example in docs runs on synthetic data.

### 2. Clinical data (`sidha.clinical`)
- Code-system crosswalks: ICD-10-CM (L73.x family + comorbidities), ICD-11,
  SNOMED CT concepts for HS and related conditions.
- Computable phenotypes: rule-based HS case definitions plus comorbidity
  phenotypes, versioned and citable so other groups can reuse them directly.
- Instrument scoring: HiSQOL and HSSD scoring functions with validation.

### 3. Diagnostics (`sidha.diagnostics`)
- Diagnostic-delay analytics: given longitudinal records, compute time from
  first HS-suggestive codes to confirmed HS diagnosis, stratified by
  demographics. This directly reproduces the published claims-data findings
  (e.g., the 5.9M-record XGBoost study, AUC 0.80) as runnable package code.
- Early-detection screener: a reference implementation of a claims/EHR-pattern
  classifier for pre-diagnosis HS risk, with documented features and evaluation.
- Differential-diagnosis ranking with the existing LLM-as-judge harness.

### 4. Public datasets (`sidha.datasets`)
Honest note: HS-specific open datasets are scarce. The package handles this
three ways:
- **Loaders for what is public:** GEO transcriptomic HS datasets (via GEOparse;
  e.g., the bulk/single-cell RNA-seq studies), and the Legit.Health-HS-IHS4
  image set (221 specialist-annotated images; loader added pending license
  confirmation).
- **A dataset catalog:** `sidha.datasets.catalog()` lists known HS data sources
  with access notes (public, gated, commercial): HS PROGRESS registry,
  TARGET-DERM, OM1 HS dataset (commercial), StuffThatWorks PROs, claims-data
  studies. Researchers see in one place what exists and how to request access.
- **A synthetic cohort generator:** realistic synthetic HS patients
  (demographics, codes, meds, flare timelines) so every tutorial, test, and demo
  runs without PHI. This is what other groups will actually run first.

### 5. Sensors (`sidha.sensors`)
- Time-series loaders for wearable exports (CSV/JSON), resampling and gap
  handling, flare-event labeling tools, and feature extraction windows aligned
  to the sensor-to-insight architecture.

## Researcher-sharing readiness

- `pip install sidha` from PyPI (name check pending), plus conda-forge and a
  Docker image for exact reproducibility.
- Docs site (MkDocs): quickstart, tutorials on synthetic data, module API
  reference, dataset catalog, phenotyping definitions.
- Tutorial notebooks runnable end-to-end with zero private data.
- Zenodo DOI per release + CITATION.cff so groups can cite it.
- Governance: code of conduct, contributing guide, issue templates, maintainer
  playbook, `good-first-issue` backlog to attract outside contributors.

## Phased build plan

- **Phase 0 (this week):** GitHub repo created, scaffold pushed, CI green,
  PyPI name reserved. Your taps: create repo, run the push commands.
- **Phase 1: DONE (Sep 14, 2026).** `ehr` + `clinical` core built and tested:
  `ehr` (ClinicalEvent/PatientTimeline, flat-CSV loader, FHIR R4 bundle
  loader, OMOP CDM loader), `clinical` (ICD-11/SNOMED crosswalks, versioned
  computable phenotypes, diagnostic-delay analytics, Hurley staging, Likert
  instrument scoring), `datasets` (synthetic cohort generator, 7-source
  dataset catalog). 29 tests passing, README quickstart updated.
  Still yours: GitHub repo creation + first push.
- **Phase 2: DONE (Sep 19, 2026).** `diagnostics`. `features` (10 documented
  EHR-pattern features from timelines), `screener` (`EarlyDetectionScreener`:
  transparent logistic-style risk scorer with reference weights, stdlib-only
  `fit()` via batch gradient descent, `evaluate()` with AUC/sens/spec/PPV/NPV,
  `threshold_sweep()`), `differential` (evidence-accumulating differential
  ranking over HS + 5 mimics with human-readable reasons), `misdiagnosis`
  (cohort-level misdiagnosis-pattern reports: per-code shares and median
  delays). 23 new tests; 52 total passing. Honest framing throughout:
  research aid, not a diagnostic device; reference weights are illustrative
  defaults, not fitted on real data.
  Still yours: GitHub repo creation + first push (see LAUNCH-CHECKLIST.md).
- **Phase 3 (next):** `datasets`. GEO loaders, IHS4 loader (license permitting),
  dataset catalog, synthetic cohort generator.
- **Phase 4:** `sensors` + `nlp` + `viz` + `privacy`. Full pipeline:
  raw data in, normalized OMOP/FHIR out, evaluated and visualized.
- **Phase 5:** Packaging and release. PyPI, conda-forge, Docker, docs site,
  v1.0 tag, Zenodo DOI, short methods note on arXiv citing the repo.

## What I need from you

1. **GitHub repo + first push** (your tap; commands below). Nothing is on
   GitHub today.
2. **Package name confirmation:** `sidha` on PyPI (checking availability next).
   If taken, fallback names ready.
3. **Clinical sign-off:** you and your supervisors verify the code crosswalks
   and phenotype definitions before v1.0. I draft, clinicians confirm.
4. **Dataset priorities:** confirm GEO-first ordering, and whether to pursue
   the IHS4 image set license.
5. **Build order approval:** Phase 1 first, or jump straight to diagnostics?

## Phase 0 commands (your tap)

```bash
cd ~/workspace/profile-building/sidha
git init -b main
git add -A && git commit -m "SIDHA scaffold: ingest, clinical, eval skeleton"
gh repo create developer-rpai/sidha --public --source=. --push
```

Then tell me it's pushed and I start Phase 1.
