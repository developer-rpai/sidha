# Changelog

## 0.2.0 (unreleased)

These notes are prep only. This is not a git tag, not a GitHub Release,
and not a PyPI publication. The version string in `pyproject.toml`,
`sidha/__init__.py`, and `CITATION.cff` is still `0.1.0`. That `0.1.0`
string on `main` was never tagged.

No Zenodo DOI is claimed. A DOI can be written down only after Zenodo
mints one for a published GitHub Release. This file does not invent one.

### Scope

The original contribution is inflammatory-disease data infrastructure.
Hidradenitis suppurativa is the flagship example (synthetic cohort,
phenotype helpers, and several sample codes). It is not a limit on which
diseases the CSV, FHIR, and OMOP loaders can read. The project name
remains SIDHA.

### What you can run

On the tree this note was written against (`main` at `7d73ee8`, plus
these prep docs):

- Install from a clone: Python >= 3.10, `pip install -e .`
- Tests: `pip install -e ".[dev]" && python -m pytest`
- Synthetic cohort demo (README "30-second demo")
- Loaders: `sidha.ehr.load_csv`, `load_bundle` (FHIR R4), `load_omop`
  (OMOP CDM CSV extracts for the five tables named in `sidha/ehr/omop.py`)
- `sidha.clinical` and `sidha.diagnostics` on those events

Synthetic fixtures in the tree:

- `data/synthetic/ehr_sample.csv`
- `data/synthetic/omop_sample/CONDITION_OCCURRENCE.csv`
- `data/synthetic/omop_sample/DRUG_EXPOSURE.csv`
- `data/synthetic/fhir_bundle_sample.json`
- `data/synthetic/hs_cases.json`

`fhir_bundle_sample.json` is a Bundle of type `collection`. One
Condition (ICD-10 E66.9) has a subject and a code and no `onsetDateTime`
or `recordedDate`. `load_bundle` skips a resource that lacks a usable
date. This note does not quote a skip count from a fresh run.

Pytest was not re-run for this commit, so no test count is stated here.
No accuracy, runtime, or cohort-size result is stated. `n_patients=200`
in the README demo is a call argument, not a measured result.

### What this release is not

- Not a sensor, wearable, NLP, visualization, or de-identification package
- Not OMOP/FHIR export (`sidha.normalize` is a placeholder). Loaders only.
- Not a patient-language taxonomy mapper, LLM judge, or metrics harness
- Not a notebook (`notebooks/` has no notebook yet)
- Not on PyPI, conda-forge, or Docker
- CI installs Python 3.11 only. `requires-python` stays `>=3.10`.
  There is no version matrix.
- Not medical advice and not a medical device
- Reference screener weights are illustrative, not fitted on patient data
- Repository contains synthetic fixtures only

### Citation

Apache-2.0. See `CITATION.cff` (still version `0.1.0`, no `doi` field).
