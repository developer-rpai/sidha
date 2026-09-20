# SIDHA Research Round 2 — Consolidated Findings

Background research for Phase 2 (diagnostics: early-detection screener) and
Phase 3 (public dataset loaders). Three parallel tracks, completed Sep 14-15,
2026. All studies, accession IDs, and package details below were verified via
web search and page reads by the research agents; nothing is invented. Where
verification was partial, it is flagged.

---

## TRACK A — HS early-detection and diagnostic ML literature

### Study 1 — Ali W, Williams J, Xiong B, Zou J, Daneshjou R (2025)
"Machine Learning for Early Detection of Hidradenitis Suppurativa: A Feasibility
Study Using Medical Insurance Claims Data." *JID Innovations* 5(3):100362.
DOI: 10.1016/j.xjidi.2025.100362 | PMID: 40226124 | PMCID: PMC11986968
(open access, full text verified)

- **Data:** Symphony Health PatientSource claims; 5.9M US individuals over
  13.5 years. 13,886 HS cases (77% female), 69,428 controls (5:1). Train
  53,362 / validation 16,611 / test 13,341. No race/ethnicity data.
- **Features:** All unaggregated billing codes as binary flags in a 24-month
  window with 6-month offset before index date, filtered to >=1% frequency
  (963 features: ICD dx, ICD procedures, HCPCS, generic drug names). A
  dermatologist-curated 113-feature clinical baseline separately.
- **Performance (test):** XGBoost AUC 0.81, F1 0.47, precision 0.34, recall
  0.75 (grid search + 5-fold CV). LR 0.75, RF 0.79, clinical baseline 0.71.
  At real-world ~2% prevalence, precision falls to ~0.05 at threshold 0.5;
  at 0.75 operating point: precision 0.15 / recall 0.35.
- **Top SHAP features:** age, sex, sulfamethoxazole/trimethoprim,
  clindamycin phosphate, obesity; also doxycycline, minocycline, ibuprofen,
  acetaminophen, incision and drainage, intralesional injections, metformin,
  benzoyl peroxide. Better performance in female and <40 subgroups.
- **Reproducibility: HIGH.** Feature engineering is trivially reproducible
  from any claims/EHR extract. Supplementary files carry the full feature
  list. No code released; data proprietary (Symphony Health, UCB-sponsored).

### Study 2 — Kirby J et al. (2024)
"Uncovering the burden of hidradenitis suppurativa misdiagnosis and
underdiagnosis: a machine learning approach." *Frontiers in Medical
Technology* 6:1200400. DOI: 10.3389/fmedt.2024.1200400 (open access)

- **Data:** IBM MarketScan 2000-2018; 55,989 HS cases; 278,483 abscess and
  1.43M cellulitis controls. Two designs: HS vs abscess, HS vs cellulitis.
- **Features:** ICD codes (3-digit prefixes), procedures via AHRQ CCS
  categories, drug classes via Red Book, age, sex.
- **Performance:** HS vs abscess AUC ~0.71; HS vs cellulitis MaxVoting AUC
  0.82 (precision 0.78, sensitivity 0.66). 1-year windows performed nearly
  as well as 3-year. Flagged up to 13% of abscess and 50% of cellulitis
  patients in some metro areas as potentially undiagnosed HS.
- **Reproducibility: HIGH** for mimic-differentiation framing. No code
  released (SAS + Python 2.7, dated). Data proprietary (AbbVie-funded).

### Study 3 — Pham H et al. (2026)
"Development of Digital Algorithms for the Early Identification of Rare
Clinical Outcomes Using Electronic Medical Records: A Case Study of
Hidradenitis Suppurativa." *Digital Health* (SAGE).
DOI: 10.1177/19427891251404892 (abstract verified)

- **Data:** Queensland tertiary-hospital EHR; 121 HS cases vs 187,106 ED
  controls; external validation at Townsville (n=168,886).
- **Features:** demographics, structured EHR, free-text diagnostic-note and
  lesion-location flags, pathology, meds, procedures, utilization.
- **Performance:** LR (threshold 0.4): sensitivity 0.66, PPV 0.71; after
  chart-audit refinement: sensitivity 0.89, PPV 0.87; external validation:
  sens/spec >0.70, PPV 0.45.
- **Reproducibility: PARTIAL.** Structured portion computable; free-text
  flags need clinical-note NLP. This is case-finding of undiagnosed HS,
  complementing the pre-diagnosis prediction of Studies 1-2.

### Study 4 — Garg A et al. (2021): HSCAPS-1
"Development and Validation of HSCAPS-1: A Clinical Decision Support Tool
for Diagnosis of Hidradenitis Suppurativa over Cutaneous Abscess."
*Dermatology* 237(5):719-726. DOI: 10.1159/000511077 (abstract verified)

- **Data:** IBM Explorys EHR (56M patients); 7,974 development, 1,560
  validation; externally validated at Penn State Health (n=2,317).
- **Features:** ~17 EHR variables: age, sex, race, BMI, smoking, T2D, acne,
  substance use, Down syndrome, opioid Rx count, sleep apnea, MI, liver
  disease, ulcerative colitis, spondyloarthritis, PCOS, depression.
- **Performance:** c-statistic (AUC) 0.746. Key ORs: female 2.17, acne
  history 3.46, Down syndrome 5.35, BMI 1.05/unit.
- **Reproducibility: VERY HIGH.** Closed-form logistic equation on common
  EHR variables; no training needed. Coefficient table must be pulled from
  the full text (abstract verified only).

### Study 5 — Kumar S et al. (2024, preprint)
CITE-seq immune profiling for HS diagnosis. Research Square rs.3.rs-4791069/v1;
PMCID: PMC11419166. NOTE: preprint, n=38 (9 HS + 29 controls).

- Reported RF/GB accuracy 100% / AUC 1.0 — not credible as validated
  performance given the tiny sample; treat as a marker-set study only
  (monocyte TNF/IL1B/NF-kB axis, IL-17/IL-26/TNF pathways).
- **Reproducibility: LOW** for the package core. Belongs in a future
  biomarker-adjunct module with explicit caveats.

### Study 6 (supporting) — Hardin J et al. (2022)
"Phenotype Algorithms to Identify Hidradenitis Suppurativa Using Real-World
Data." *JMIR Dermatology* 5(4):e38783. DOI: 10.2196/38783.

- Validated HS case-finding algorithms: >=2 HS codes gives mean PPV 86%;
  >=1 code gives mean sensitivity 58%. SIDHA's phenotyper should implement
  the >=2-code option and expose the tradeoff.

### Cross-study feature families (most predictive first)
1. Age at prediction; 2. Sex (female predominance); 3. Antibiotic exposure
   (TMP-SMX, clindamycin, doxycycline, minocycline, isotretinoin);
4. Mimic/symptom codes (abscess, cellulitis, acne, pilonidal, follicular
   disorders); 5. Procedures (incision and drainage, culture, intralesional
   injections); 6. Metabolic cluster (obesity, T2D, PCOS, dyslipidemia);
7. Pain/utilization (opioid counts, dermatology visits, ED patterns);
8. Inflammatory labs (EHR only); 9. Free-text lesion-location notes (needs
   NLP); 10. Immune biomarkers (adjunct only).

### Key meta-finding
**No study released code.** SIDHA's re-implementations would be the first
open implementations of all of these approaches. All claims data are
proprietary, so the package ships model code + feature definitions but not
trained weights.

---

## TRACK B — Public HS dataset inventory with loader feasibility

All GEO accession IDs and sample counts verified via live NCBI E-utilities
queries. Nothing invented.

### GEO transcriptomic datasets — open, GEOparse-loadable now
| Accession | Design | Samples | Verdict |
|---|---|---|---|
| GSE151243 | Bulk RNA-seq, paired lesional/nonlesional (UNC/Sayed) | 40 | Ship loader now — canonical set |
| GSE155176 | Bulk, lesional/nonlesional/healthy + treatment states | 87 | Ship loader now — largest bulk set |
| GSE154773 | Bulk, dual tissue skin + blood | 63 | Ship loader now |
| GSE213761 | Bulk, longitudinal anti-TNF treatment response | 59 | Ship loader now |
| GSE245451 | Bulk, lesion/perilesional/healthy (NLRP3 paper) | 16 | Ship loader now |
| GSE128637 | Microarray | 21 | Ship loader now |
| GSE72702 | Microarray | 30 | Ship loader now |
| GSE154775 | scRNA-seq | 9 | Caveats: no series matrix; parse supplementary files |
| GSE175990 | scRNA-seq | 4 | Same caveat |
| GSE220116 | scRNA-seq, mixed HS/psoriasis/controls | ~8 HS of 36 | Caveats: subset by GSM title pattern |

Access path for all: GEO query page by accession, or
`GEOparse.get_GEO(geo="GSE...")` from NCBI FTP. The 2025 PLOS ONE
biomarker-ML paper reused GSE154773, GSE155176, GSE213761, GSE128637,
GSE220116, GSE175990, GSE154775 — confirming these are the working sets
the field actually uses.

### Legit.Health-HS-IHS4 image set — NOT downloadable
221 HS lesion images, IHS4-annotated by six dermatologists
(DOI 10.1111/srt.13357, paper is open access). The dataset itself was
**never released**: no download link, GitHub, Zenodo, or Hugging Face
found. Contact: Ignacio Hernandez Montilla,
ignaciohernandez@legit.health (from the paper). Expect a commercial or
negotiated academic response (Legit.Health sells AIHS4 scoring via API).
**Verdict: catalog entry only**, with the contact recorded.

### Other imaging sources — no HS bulk download anywhere
- DermNet NZ: individual HS images, per-image licensing ("fees apply").
  Catalog entry only.
- ISIC Archive: no HS class exists; off-target. Not applicable.
- Wiala et al. 777-image HS severity set: paper only, not released.
- SCGAN/DermSynth3D/DermaSynth synthetic sets: melanoma/nevus-focused,
  method references only.

### PRO / survey datasets — none open
- StuffThatWorks HS cohort (~1,050 patients): gated behind a fellowship
  program / commercial licensing. No download. Catalog entry only.
- **No open HS PRO/survey dataset exists** as far as verified. Genuine
  gap; the package docs should state this rather than imply coverage.

### Gated / commercial sources — catalog entries only
HS PROGRESS (UCSF, ~500+ enrolled, target 8,000; consortium proposal
required), TARGET-DERM HS cohort (Target RWE commercial licensing),
OM1 HS dataset (~26k records, commercial), AAD DataDerm (institutional
access).

### Synthetic EHR — build, don't wrap
Synthea (MITRE, Apache 2.0) has 107 modules but **no HS module**
(only `dermatitis.json`). The high-value move: author a Synthea
`hidradenitis_suppurativa.json` module (post-puberty onset; obesity,
metabolic syndrome, depression, IBD comorbidities; dermatology and
biologic encounters) so `sidha` generates realistic synthetic EHR cohorts
via its existing CSV loaders. Synthea is Java; Python-side integration is
"run Synthea, load CSVs."

### Honesty section — "public" but not actually downloadable
- CITE-seq HS study (PMC11419166): Data Availability reads "GSE194315 for
  healthy and **GSEXXX for HS samples**" — the HS accession was never
  disclosed. GSE194315 is a spondyloarthritis study. HS CITE-seq data
  effectively unavailable.
- IHS4 image set: open-access paper, unreleased data; DermQuest source
  images gone (service shut down).
- Platform/instrument models for GEO sets could not be verified beyond
  GSE151243's "Illumina paired-end" — report data type, not instrument.

---

## TRACK C — Exemplary disease-specific Python research packages

Four packages verified via GitHub pages, READMEs, and commit histories.
Deliberate finding: **no maintained open-source Python package exists for
skin/dermatology research data** (only one-off student repos) — SIDHA has
a clear field.

### 1. YASA (sleep analysis) — https://github.com/raphaelvallat/yasa
~584 stars; eLife 2021 paper; maintained (v0.7.0 in 2026). Patterns:
`fetchers.py` data-download module + 10-minute quickstart tutorial as the
README onboarding path; FAQ page answering data-format questions;
optional-extras packaging (`yasa[full]`) keeping the core light; numbered
tutorial notebooks (01-20) + visual plot gallery; PyPI + conda-forge;
pytest + GitHub Actions + Codecov + Ruff.

### 2. Clinica (neurodegenerative neuroimaging) — https://github.com/aramis-lab/clinica
~290 stars; Front. Neuroinform. 2021 paper; standing lab team. Patterns:
one-module-per-dataset converters (`adni_to_bids/`, ...) behind a shared
abstract contract with uniform CLI; three test tiers
(unit/nonregression/instantiation); anchor to a community data standard
(BIDS) as the interoperability pitch; per-converter and per-pipeline doc
pages; PyPI + conda env; Google Group + GitHub Discussions community.

### 3. epilepsy2bids (epilepsy EEG) — https://github.com/esl-epfl/epilepsy2bids
Real downstream use (NeurIPS 2025 seizure-detection pipelines, SzCORE
validation CI). Patterns: 3-line `convert()` contract per dataset with an
explicit "how to add a new dataset" section; **tiny sample data files
embedded in `tests/`** so all tests run offline with zero downloads;
domain classes (`Eeg`, `Annotation`) as first-class API; README-only docs
suffice when the API surface is tiny.

### 4. iglu_python (diabetes CGM metrics) — https://github.com/staskh/iglu_python
Python port of the R `iglu` research standard; commercially sponsored.
Patterns: **reference-validation compatibility table** in the README
(every function vs the R original at 0.001 precision, via
`tests/expected_results.json`); canonical input schema (`id`/`time`/`gl`)
+ vendor-specific loaders; honest "Known Implementation Differences"
docs; README examples on synthetic `np.random` data so everything runs
with zero real data.

### Ranked patterns SIDHA should copy
1. `sidha/datasets/<source>/` modules with a uniform `fetch()`/`convert()`
   contract + an "adding a new dataset" section (Clinica, epilepsy2bids).
2. Every test and tutorial runs offline on embedded synthetic/sample data
   with zero downloads (epilepsy2bids sample files; SIDHA already has the
   synthetic generator — wire it as the default everywhere).
3. `fetch_*()` downloaders caching to `~/.cache/sidha` + `load_synthetic()`
   fallback in every tutorial (YASA fetchers, iglu synthetic examples).
4. Reference-validation compatibility table in the README: validate
   phenotypes and diagnostic-delay metrics against published HS
   definitions/cohorts and show the table (iglu_python).
5. FAQ page answering data-format questions once ("how do I load my
   EHR/CSV/FHIR data?") instead of in issues (YASA).
6. Numbered tutorial notebooks + README visual gallery; a 10-minute path:
   install, load synthetic cohort, phenotype, plot (YASA, Clinica).
7. Formalize the stdlib-only core with optional extras
   (`pip install "sidha[geo]"`, `sidha[imaging]`) later (YASA).
8. PyPI + conda-forge, tagged releases, explicit supported-Python matrix;
   verify and reserve the `sidha` PyPI name (YASA, Clinica).
9. Three-tier testing: unit + non-regression + CLI/API instantiation tests
   on GitHub Actions with coverage (Clinica, YASA, iglu).
10. Citable artifact early: plan the software paper (e.g., JOSS) as the
    citation anchor; prominent "Cite us" section with DOI + Zenodo +
    CITATION.cff (YASA, Clinica).
11. Domain objects as tutorial protagonists: add convenience methods to
    `ClinicalEvent`/`PatientTimeline` (`.describe()`, `.plot_timeline()`)
    (YASA's `Hypnogram`, epilepsy2bids' `Eeg`).
12. Name the interoperability standard loudly: "any FHIR R4 / OMOP CDM /
    flat-CSV HS extract loads with one call" on the README and docs
    landing page (Clinica's BIDS pitch).

---

## Recommendations for SIDHA Phase 2 (diagnostics)

1. **Re-implement Ali et al. (2025) first** as `sidha.diagnostics.screener`:
   24-month lookback window with 6-month offset before index date; binary
   ICD/drug presence flags with >=1% prevalence filter; age/sex; XGBoost
   or logistic regression interface. Reference performance: test AUC 0.81,
   recall 0.75, precision 0.34. Fully computable from standard extracts.
2. **Add HSCAPS-1** as a lightweight no-training screener (~17 EHR
   variables, c-statistic 0.746). Needs the coefficient table from the
   full text (abstract verified only).
3. **Add the Kirby lane second:** HS-vs-abscess/cellulitis
   differentiation as the screener's second stage (MaxVoting AUC 0.82 on
   the cellulitis cohort).
4. **Expose operating-point tuning, never bake in a threshold.** Report
   AUC/F1/precision/recall at multiple thresholds and document the
   prevalence-adjusted precision honestly (0.05 at 2% prevalence,
   threshold 0.5).
5. **Ship model code + feature definitions, not trained weights.** No
   public HS claims dataset exists to benchmark against; models train on
   the user's own extracts or run on synthetic data. Document this
   explicitly.
6. **Biomarker adjunct later:** CITE-seq markers belong in a future
   module with explicit caveats (preprint, n=38), not in the core
   screener.

## Recommendations for SIDHA Phase 3 (dataset loaders)

1. Build `sidha/datasets/gse151243/`, `gse155176/`, `gse154773/` first
   (bulk RNA-seq, GEOparse, loadable now), each implementing the uniform
   `fetch()`/`convert()` contract; add GSE213761, GSE245451, GSE128637,
   GSE72702 next; scRNA trio (GSE154775, GSE175990, GSE220116) with
   documented caveats and HS-sample subsetting for GSE220116.
2. `fetch_*()` functions cache to `~/.cache/sidha`; every tutorial uses
   `load_synthetic()` fallback so nothing requires a download.
3. Catalog entries (no loaders) for: IHS4 (with author contact
   ignaciohernandez@legit.health), DermNetNZ, Wiala set, StuffThatWorks,
   HS PROGRESS, TARGET-DERM, OM1, DataDerm, ISIC (noted as no HS class).
4. Author a Synthea HS module (`hidradenitis_suppurativa.json`) — a new
   contribution the field lacks — and document the "run Synthea, load
   CSVs" path.
5. Docs honesty section: state plainly that no open HS PRO dataset and
   no downloadable HS image set exist; position the package as the reason
   that changes.

## Cross-cutting (from Track C)
- Formalize extras packaging; verify/reserve the PyPI `sidha` name.
- Numbered tutorials + FAQ + reference-validation table in README.
- Three-tier tests on GitHub Actions; numbered-notebook gallery.
- Start the JOSS software-paper outline early as the citation anchor.

---

## Open questions
1. HSCAPS-1 coefficients: full text needed to extract the 17-variable
   equation (abstract verified only).
2. GEO scRNA loaders: confirm GEOparse/supplementary-file behavior for
   GSE154775, GSE175990, GSE220116 with a live fetch test.
3. IHS4 access: user decision on emailing ignaciohernandez@legit.health
   (fits the email-only, collaboration-first outreach rule).
4. Synthea HS module: JSON authoring needs clinical review before
   release.
5. PyPI name `sidha` availability still unverified (browser fetch failed
   Sep 14).
6. Operating-point conventions for the screener: defer threshold choices
   to the user/clinician rather than baking them in.
7. Race/ethnicity is absent from the underlying claims data — limits
   equity/bias evaluation the package can honestly offer.
8. JOSS software-paper timing relative to the v1.0 release.
