# SIDHA roadmap

Scope: inflammatory-disease data infrastructure. Hidradenitis suppurativa
is the flagship example. The project name stays SIDHA.

The public repository is [developer-rpai/sidha](https://github.com/developer-rpai/sidha),
default branch `main`. The package version string on `main` is still
`0.1.0`. That string was never tagged, and there is no GitHub Release.
A first tag is planned as **v0.2.0** and is not cut on this branch.
No Zenodo DOI exists. Do not treat a "v0.1 release" line as something
that already happened.

This page used to be titled "90-Day Roadmap — to v0.1" and still described
a local-only scaffold. Boxes below are corrected only where `main`
already contains the work. Items that are still absent stay open.

## Weeks 1–2 — Scaffold and announce

- [x] Repo scaffold (README, LICENSE, package layout, CI, contributing guide)
- [x] Public repo on GitHub (`developer-rpai/sidha`); `main` is pushed
- [ ] README architecture diagram + quickstart verified on a clean machine
- [ ] Announce intent on OHDSI forums + relevant workgroup calls

## Weeks 3–4 — Ingest and clinical coding

- [x] `ingest`: Reddit collector for public HS discussion (provenance-logged)
- [ ] `ingest`: X collector (public posts, ToS-compliant)
- [x] `ehr`: flat CSV loader and synthetic fixture (`data/synthetic/ehr_sample.csv`)
- [x] `clinical`: ICD-10 mapping module (L73.x hidradenitis family + common comorbidities)
- [x] Unit tests for clinical and ICD mapping on synthetic fixtures are in `tests/`.
  This page does not quote a pytest summary. Pytest was not re-run for the
  prep commit that corrected this file.

## Weeks 5–8 — Taxonomy mapper and normalization (not done)

- [ ] `taxonomy`: patient-language → clinical-taxonomy mapper v1
  (lexicon + rules baseline; embedding upgrade path documented)
- [ ] `normalize`: OMOP CDM output (Condition_Occurrence, Observation, Drug_Exposure)
- [ ] `normalize`: FHIR R4 output (Condition, Observation, MedicationStatement)
- [ ] Round-trip test: synthetic vignette → OMOP + FHIR, validated against profiles
- [ ] Label bite-size follow-ups `good first issue` (the label on this repo uses spaces)

## Weeks 9–12 — Judge harness (not done)

- [ ] `judge`: LLM-as-judge differential-diagnosis harness (prompt templates + rubric)
- [ ] `eval`: synthetic golden test set (hand-built vignettes, known-correct rankings)
- [ ] `eval`: ranking metrics (top-k accuracy, MRR on differential lists)
- [ ] Docs site pass; end-to-end demo notebook on synthetic data

## Citation and first tag (not done)

These used to be listed as a finished v0.1 release and a Zenodo DOI
"from day one". Neither has happened.

- [ ] Cut the first git tag and GitHub Release as `v0.2.0` (not as a
  belated `v0.1.0`; `0.1.0` stays the unreleased version string that was on `main`)
- [ ] Mint a Zenodo DOI only after that Release is published and Zenodo
  archives it. Do not write a guessed DOI into `CITATION.cff`.
- [ ] Keep a `good first issue` backlog for outside contributors

## Ongoing

- Short methods note (arXiv) citing the repo, after there is a citable release
- Demo at OHDSI/FHIR community calls; link from workgroup pages
- Fast reviews, clear issues, and a public roadmap for outside contributors
