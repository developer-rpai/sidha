# SIDHA Big Package Plan — from scaffold to `pip install sidha`

Goal: turn the SIDHA scaffold into a robust, researcher-ready Python package that
other research groups can install, run, and extend. One package, many
functionalities: EHR ingestion, clinical coding and phenotyping, diagnostic
support, sensor streams, public dataset loaders, normalization to open standards,
and reproducible evaluation.

Scope note (prep, 2026-10-03): this is inflammatory-disease data
infrastructure. Hidradenitis suppurativa is the flagship example in the
phenotypes, fixtures, and synthetic demo. That example is not a claim that
the loaders only accept HS data. The name SIDHA is unchanged. Nothing in
this file is a published release, and there is no Zenodo DOI.

## Where things stand today

- The project is public at `https://github.com/developer-rpai/sidha` on
  branch `main`. It is not a local-only scaffold, and it has been pushed.
  An earlier draft of this file said the tree lived only at
  `~/workspace/profile-building/sidha` and that nothing had been pushed.
  That is no longer true. Do not re-run the old `git init` / `gh repo create`
  commands.
- Package version string on `main` is `0.1.0` (`pyproject.toml`,
  `sidha/__init__.py`, `CITATION.cff`). There is no git tag and no GitHub
  Release. The prep branch does not bump that string and does not add a DOI.
- Modules that run: `ehr` (CSV, FHIR R4 Bundle, OMOP CDM CSV loaders),
  `clinical`, `diagnostics`, `datasets` (synthetic cohort generator and a
  source catalog), `ingest` (Reddit collector behind the `social` extra).
  `taxonomy`, `normalize`, `judge`, and `eval` are still docstring-only
  placeholders. There is no `sensors` package.
- An earlier draft of this plan said "11 passing tests". The README on
  `main` stated "52 tests". This prep edit does not re-run pytest and does
  not add a new count.
- This plan still describes the larger package below. It does not replace
  [ROADMAP.md](ROADMAP.md).

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

`sensors`, `nlp`, `viz`, and `privacy` are not in the tree. `normalize`,
`eval`, and `judge` are placeholders. Do not read this diagram as shipped code.

## Data coverage: what the package will handle

### 1. EHR data (`sidha.ehr`)

- Loaders for FHIR R4 Bundle JSON, OMOP CDM table extracts (CSV/Parquet),
  and flat clinical-record CSVs with a documented schema. Parquet is not
  implemented.
- Patient-journey builder: longitudinal record -> ordered event timeline per
  patient (encounters, conditions, meds, procedures).
- All loaders are format-first. They are not limited to HS codes. Every
  example in docs runs on synthetic data.

### 2. Clinical data (`sidha.clinical`)

- Code-system crosswalks: ICD-10-CM (L73.x family + comorbidities), ICD-11,
  SNOMED CT concepts for HS and related conditions. HS is the flagship
  example of a broader inflammatory-disease coding surface.
- Computable phenotypes: rule-based HS case definitions plus comorbidity
  phenotypes, versioned and citable so other groups can reuse them directly.
- Instrument scoring: HiSQOL and HSSD scoring functions with validation.

### 3. Diagnostics (`sidha.diagnostics`)

- Diagnostic-delay analytics: given longitudinal records, compute time from
  first suggestive codes to a confirmed diagnosis, with HS as the flagship
  case definition.
- Early-detection screener: a reference implementation of an EHR-pattern
  scorer, with documented features. Reference weights are illustrative,
  not fitted on patient data. This file does not add accuracy or cohort-size
  claims.
- Differential-diagnosis ranking. The LLM-as-judge harness is not implemented
  (`sidha.judge` is a placeholder).

### 4. Public datasets (`sidha.datasets`)

Honest note: HS-specific open datasets are scarce. The package handles this
three ways:

- **Loaders for what is public:** GEO transcriptomic datasets are still
  planned. The catalog's only `loader: available` row is the synthetic cohort.
- **A dataset catalog:** `sidha.datasets` lists known sources with access
  notes. Researchers see in one place what exists and how to request access.
- **A synthetic cohort generator:** synthetic patients so every tutorial,
  test, and demo runs without real patient data. The generator shipped with
  the HS flagship example. It is already on `main`.

### 5. Sensors (`sidha.sensors`)

Not in the tree. Planned later: time-series loaders for wearable exports,
resampling and gap handling, flare-event labeling, and feature windows.

## Researcher-sharing readiness

- `pip install sidha` from PyPI is not available. The name was unclaimed at
  inspection on 2026-10-03. Re-check before any publish. Conda-forge and
  Docker are not in scope for the unreleased 0.2.0 prep.
- Docs site (MkDocs) is not built.
- Tutorial notebooks: `notebooks/` has no notebook yet.
- Zenodo DOI: not minted. `CITATION.cff` has no `doi` field.
- Governance: contributing guide exists. Issue label for newcomers is
  `good first issue` (spaces), not `good-first-issue`.

## Phased build plan

- **Phase 0:** done. The GitHub repo exists and `main` is pushed. Do not
  run the historical create commands again.
- **Phase 1: on `main`.** `ehr` + `clinical` core: ClinicalEvent /
  PatientTimeline, flat-CSV loader, FHIR R4 bundle loader, OMOP CDM loader,
  ICD-11/SNOMED crosswalks, versioned computable phenotypes,
  diagnostic-delay analytics, Hurley staging, Likert instrument scoring,
  synthetic cohort generator, dataset catalog. The public repo is no longer
  a pending "first push".
- **Phase 2: on `main`.** `diagnostics`: documented EHR-pattern features,
  `EarlyDetectionScreener` (reference weights, `fit()`, `evaluate()`),
  differential ranking, misdiagnosis-pattern reports. Research aid, not a
  diagnostic device. Reference weights are illustrative defaults, not fitted
  on real data. This section does not quote a test total.
- **Phase 3 (next):** public dataset loaders (GEO, and an image loader only
  if the license allows) and catalog expansion. The synthetic cohort
  generator is already on `main`. It is not still pending.
- **Phase 4:** `sensors` + `nlp` + `viz` + `privacy`. Not in the tree.
- **Phase 5:** Packaging and release. PyPI, conda-forge, Docker, docs site,
  v1.0 tag, Zenodo DOI, short methods note. Not part of this prep branch.
  A first tag, if cut later, is v0.2.0, not a retroactive v0.1.0.

## What is still a human decision

1. **Version bump, tag, and GitHub Release** for v0.2.0. Not done here.
2. **Package name confirmation:** `sidha` on PyPI. Re-check the day you
   publish. This prep does not publish.
3. **Clinical review** of crosswalks and phenotype definitions before a
   1.0 claim. Drafts are in the tree; confirmation is not.
4. **Dataset priorities:** GEO-first ordering, and whether to pursue an
   image-set license.
5. **Zenodo:** toggle the GitHub integration on before any Release you
   want archived. Do not write a DOI before Zenodo shows one.

## Phase 0 commands (historical — do not re-run)

These commands were the original tap. The repository already exists.
Running them again would fight the current `main` history.

```bash
cd ~/workspace/profile-building/sidha
git init -b main
git add -A && git commit -m "SIDHA scaffold: ingest, clinical, eval skeleton"
gh repo create developer-rpai/sidha --public --source=. --push
```

Phase 1 and Phase 2 are already on `main`. This section is not the current tap.
