# SIDHA 90-Day Roadmap — to v0.1

Target: a public, CI-tested, documented v0.1 that a stranger can clone, install,
and run end-to-end on synthetic data.

## Weeks 1–2 — Scaffold & announce
- [x] Repo scaffold (README, LICENSE, package layout, CI, contributing guide)
- [ ] Create public repo on GitHub (`developer-rpai/sidha`), push scaffold
- [ ] README architecture diagram + quickstart verified on a clean machine
- [ ] Announce intent on OHDSI forums + relevant workgroup calls
- [ ] Mint Zenodo DOI for the first release tag (citable from day one)

## Weeks 3–4 — Ingest + clinical coding
- [x] `ingest`: Reddit collector for public HS discussion (provenance-logged)
- [ ] `ingest`: X collector (public posts, ToS-compliant)
- [ ] `ingest`: episodic clinical-record loader (CSV shape defined, synthetic fixture)
- [x] `clinical`: ICD-10 mapping module (L73.x hidradenitis family + common comorbidities)
- [ ] Unit tests for mapping coverage on synthetic fixtures

## Weeks 5–8 — Taxonomy mapper + normalization (the core)
- [ ] `taxonomy`: patient-language → clinical-taxonomy mapper v1
  (lexicon + rules baseline; embedding upgrade path documented)
- [ ] `normalize`: OMOP CDM output (Condition_Occurrence, Observation, Drug_Exposure)
- [ ] `normalize`: FHIR R4 output (Condition, Observation, MedicationStatement)
- [ ] Round-trip test: synthetic vignette → OMOP + FHIR, validated against profiles
- [ ] Label bite-size follow-ups `good-first-issue`

## Weeks 9–12 — Judge harness + v0.1 release
- [ ] `judge`: LLM-as-judge differential-diagnosis harness (prompt templates + rubric)
- [ ] `eval`: synthetic golden test set (hand-built vignettes, known-correct rankings)
- [ ] `eval`: ranking metrics (top-k accuracy, MRR on differential lists)
- [ ] Docs site pass; end-to-end demo notebook on synthetic data
- [ ] **v0.1 release** + write-up post (OHDSI forum / personal blog)
- [ ] Open `good-first-issue` backlog to attract outside contributors

## Ongoing (evidence mechanics)
- GitHub stars/forks as adoption signal; Zenodo DOI per release
- Short methods note (arXiv) citing the repo
- Demo at OHDSI/FHIR community calls; link from workgroup pages
- Being a maintainer others contribute to is itself EB1A evidence — keep the
  contributor ladder greased: fast reviews, clear issues, public roadmap
