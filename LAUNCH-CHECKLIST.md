# SIDHA Launch Checklist

Everything below is **your tap** — in order. The code is built, tested
(52 tests green), and ready to push.

## 1. Create the GitHub repo and push

```bash
cd ~/workspace/profile-building/sidha
git init -b main
git add -A
git commit -m "SIDHA: ehr, clinical, diagnostics core (52 tests)"
gh repo create developer-rpai/sidha --public --source=. --push
```

Verify: open https://github.com/developer-rpai/sidha — the README should
render with the architecture diagram and quickstart.

> Do **not** add the `.venv/` directory if `git add -A` picks it up —
> `.gitignore` already excludes it. Double-check with `git status` before
> committing.

## 2. Confirm CI is green

The `.github/workflows/` CI runs the install check + pytest on push.
Watch the first run on the repo's Actions tab; it should be green in a
few minutes. If red, paste me the log.

## 3. Check the PyPI name

```bash
pip index versions sidha   # or check https://pypi.org/project/sidha/
```

- If **available**: nothing to do yet — publishing is a Phase 5 step.
  (Do not publish now; the plan is PyPI at v1.0 with the docs site.)
- If **taken**: tell me and I'll rename the package metadata
  (fallback candidates: `sidha-hs`, `hs-sidha`) before anything public
  hardens around the name.

## 4. Optional but recommended (same day)

- [ ] **Pin the repo** on your GitHub profile
  (Profile → Customize your pins → add `developer-rpai/sidha`).
- [ ] **Topics**: add `hidradenitis-suppurativa`, `omop-cdm`, `fhir`,
  `health-data`, `digital-health` on the repo's About section.
- [ ] **About description**: "Open data architecture for hidradenitis
  suppurativa research: EHR ingestion, computable phenotypes,
  early-detection screening, OMOP/FHIR normalization."
- [ ] **Post the announcement** (LinkedIn + OHDSI forum drafts live with
  the rest of your promo posts).

## 5. After launch — what I pick back up

- Phase 3 build (GEO loaders, dataset catalog expansion).
- `good-first-issue` backlog seeding for outside contributors.
- Docs site (MkDocs) + tutorial notebooks on synthetic data.
- Monitoring the repo for issues/stars; first external contributor PR.

## Explicitly NOT doing now

- No PyPI publish (Phase 5).
- No conda-forge / Docker (Phase 5).
- No Zenodo DOI (at v1.0 tag).
