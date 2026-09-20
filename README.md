# SIDHA — Sensor-to-Insight Data for Hidradenitis Suppurativa Architecture

An open reference implementation for turning **episodic clinical records** and
**public social-listening data** into continuous, research-ready hidradenitis
suppurativa (HS) intelligence.

## Why this exists

Hidradenitis suppurativa carries one of the longest diagnostic delays in
dermatology — patients routinely wait the better part of a decade between
first symptoms and a correct diagnosis, cycling through abscess, acne, and
pilonidal-disease codes along the way. Meanwhile, rich signals about early
symptoms, flare patterns, and treatment experience sit scattered across
clinical records, registries, and public patient discussions, in formats no
researcher can query together.

SIDHA is a data architecture for closing that gap: ingest heterogeneous HS
data, map everyday patient language to clinical taxonomies, quantify
diagnostic delay, score early-detection risk from EHR patterns, normalize
everything to open health-data standards (OMOP CDM, FHIR R4), and evaluate
analytic approaches reproducibly.

There is currently **no actively maintained HS-specific open-source project**.
SIDHA aims to be that shared foundation.

## What you can do with it today

- **Load records** from flat CSVs, FHIR R4 Bundles, or OMOP CDM extracts
  (`sidha.ehr`).
- **Phenotype cohorts** with versioned, citable HS case definitions,
  comorbidity profiles, Hurley staging helpers, and HiSQOL/HSSD instrument
  scoring (`sidha.clinical`).
- **Measure diagnostic delay** from first suggestive code to confirmed
  diagnosis, and generate cohort-level **misdiagnosis-pattern reports**
  (`sidha.clinical`, `sidha.diagnostics`).
- **Screen for pre-diagnosis risk** with `EarlyDetectionScreener`, a
  transparent logistic-style scorer over documented EHR features — with
  reference weights for exploration and a `fit()` method to calibrate on
  your own labeled cohort (`sidha.diagnostics`).
- **Rank differential diagnoses** with an evidence-accumulating, fully
  explainable baseline (`sidha.diagnostics`).
- **Work on synthetic data** — a seeded synthetic HS cohort generator means
  every tutorial, test, and demo runs with zero PHI (`sidha.datasets`).
- **Normalize** to OMOP CDM and FHIR R4 builders (`sidha.normalize`).

## Quickstart

```bash
pip install sidha        # once published; for now: pip install -e .
python -c "import sidha; print(sidha.__version__)"
```

End-to-end on synthetic data — no PHI, no setup:

```python
from sidha.datasets import generate_cohort
from sidha.ehr import build_timelines
from sidha.clinical import summarize_cohort
from sidha.diagnostics import (
    EarlyDetectionScreener, evaluate, misdiagnosis_report, rank_differentials,
)

# 1. Synthetic cohort (deterministic) -> patient timelines
events = generate_cohort(n_patients=200, seed=99)
timelines = list(build_timelines(events).values())

# 2. Cohort summary: case counts + mean diagnostic delay
print(summarize_cohort(timelines))

# 3. What gets misdiagnosed, and how long does it take?
print(misdiagnosis_report(timelines)["median_delay_days_overall"])

# 4. Early-detection screening on one patient
screener = EarlyDetectionScreener()          # reference weights
print(f"risk score: {screener.score(timelines[0]):.3f}")
print(screener.feature_contributions(timelines[0])[:3])  # why

# 5. Differential ranking with evidence reasons
for cand in rank_differentials(timelines[0])[:3]:
    print(f"{cand.name}: {cand.score:.1f} — {cand.supporting[0] if cand.supporting else 'no evidence'}")
```

Bring your own records:

```python
from sidha.ehr import load_csv, load_bundle, load_omop

events = load_csv("records.csv")             # documented schema, see module docs
events, report = load_bundle("bundle.json")  # FHIR R4
events, report = load_omop("omop_tables/")   # OMOP CDM v5.x CSVs
```

Calibrate the screener on your own labeled cohort:

```python
screener = EarlyDetectionScreener().fit(timelines, labels)  # 1 = HS case
print(evaluate(screener, timelines, labels))
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│   ingest    │────▶│   clinical   │────▶│    diagnostics    │
│ public      │     │ ICD-10/11,   │     │ screener,         │
│ social +    │     │ SNOMED,      │     │ differential      │
│ episodic    │     │ phenotypes,  │     │ ranking,          │
│ records     │     │ instruments  │     │ misdiagnosis      │
└─────────────┘     └──────────────┘     └────────┬──────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│    eval     │◀────│    judge     │◀────│    normalize      │
│ metrics +   │     │ LLM-as-judge │     │ OMOP CDM +        │
│ synthetic   │     │ differential-│     │ FHIR R4 output    │
│ golden sets │     │ dx harness   │     │                   │
└─────────────┘     └──────────────┘     └───────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design and
[docs/BIG-PACKAGE-PLAN.md](docs/BIG-PACKAGE-PLAN.md) for the v1.0 build plan.

## Repository layout

```
sidha/
├── sidha/               # Python package (stdlib-only core)
│   ├── ingest/          # public social-listening collectors + record loaders
│   ├── ehr/             # EHR loaders: flat CSV, FHIR R4 bundles, OMOP CDM
│   ├── clinical/        # ICD-10/ICD-11/SNOMED crosswalks, computable
│   │                    # phenotypes, diagnostic-delay analytics, instruments
│   ├── diagnostics/     # early-detection screener, differential ranking,
│   │                    # misdiagnosis reports
│   ├── datasets/        # dataset catalog + synthetic cohort generator
│   ├── taxonomy/        # patient-language → clinical-taxonomy mapper
│   ├── normalize/       # OMOP CDM + FHIR R4 normalization layer
│   ├── judge/           # LLM-as-judge differential-diagnosis eval harness
│   └── eval/            # metrics + synthetic golden test sets
├── notebooks/           # exploratory analyses
├── data/                # synthetic/sample data ONLY (never real data)
├── docs/                # architecture + roadmap + big-package plan
└── tests/               # 52 tests, all on synthetic data
```

## Roadmap

- **Phase 1 (done):** `ehr` + `clinical` core — timelines, loaders, crosswalks,
  versioned phenotypes, diagnostic-delay analytics, instruments, synthetic
  cohort generator.
- **Phase 2 (done):** `diagnostics` — early-detection screener, differential
  ranking, misdiagnosis reports.
- **Phase 3:** public dataset loaders (GEO transcriptomics), dataset catalog
  expansion.
- **Phase 4:** `sensors` + `nlp` + `viz` + `privacy` — full sensor-to-insight
  pipeline.
- **Phase 5:** PyPI release, docs site, v1.0 tag, Zenodo DOI.

The detailed checklist lives in [docs/ROADMAP.md](docs/ROADMAP.md).
`good-first-issue` labels mark bite-size entry points for outside contributors.

## Contributing

Contributions are welcome — code, documentation, dataset ideas, and evaluation
design. See [CONTRIBUTING.md](CONTRIBUTING.md). Ground rules: public/synthetic
data only, no medical-advice framing, standards (OMOP/FHIR) first.

## Citation

If you use SIDHA in research, please cite it (see [CITATION.cff](CITATION.cff)).

## License

Apache-2.0 — see [LICENSE](LICENSE).

## Disclaimer

SIDHA is a **research reference implementation**, not a medical device and not
medical advice. The early-detection screener's reference weights are
illustrative defaults, not fitted on real patient data — calibrate on your own
labeled cohort before any research use. This repository contains **no real
patient data** — only synthetic or sample data. Any clinical application
requires appropriate validation, oversight, and data-use agreements.
