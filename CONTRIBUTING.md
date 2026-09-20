# Contributing to SIDHA

Thank you for your interest in contributing. SIDHA is an open research
reference implementation, and community contributions — code, documentation,
dataset curation ideas, and evaluation design — are all welcome.

## Ground rules

- **Public data only.** Never submit real patient data, credentials, API keys,
  or anything covered by a data-use agreement. The `data/` directory accepts
  synthetic or sample data only.
- **No medical advice.** This is a research architecture, not a diagnostic tool.
  Frame contributions accordingly.
- **Standards first.** Prefer OMOP CDM and FHIR R4 representations; document
  any deviation in an Architecture Decision Record under `docs/`.

## How to contribute

1. Fork the repo and create a branch from `main`.
2. Issues labeled **`good-first-issue`** are scoped, bite-size entry points —
   start there if you're new.
3. Open a pull request with a clear description of what changed and why.
   Small, focused PRs get reviewed fastest.
4. CI must pass (install check + syntax compile). Add tests where behavior
   is non-trivial.

## Code style

- Python 3.10+, type hints on public functions, docstrings on modules.
- Keep modules dependency-light; heavy ML dependencies belong behind
  optional extras.

## Questions?

Open a GitHub issue — design discussions are welcome before code.
