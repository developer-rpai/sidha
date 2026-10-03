# sidha-fixture-shape-check

Proposed n8n workflow name: `sidha-fixture-shape-check`.

This directory is a note, not a finished workflow. There is no
`sidha-fixture-shape-check.json` in the repo yet, and no n8n execution
has been recorded. Do not treat this page as a pass/fail result.

The check is about the synthetic fixture shape that `sidha.ehr` already
loads. It is inflammatory-disease data infrastructure: hidradenitis
suppurativa codes in the samples are the flagship example, not a rule
that other diseases fail the check. It is not an OHDSI
DataQualityDashboard run and not a full OMOP CDM or FHIR profile
validator.

Apache-2.0, same as the rest of SIDHA. Synthetic fixtures only. No token.
The files are public.

Warp is only one editor you might use to write the export later. The
workflow does not depend on Warp, and this repo does not ship a Warp
Drive file.

## What a later import would do

When someone adds the JSON export:

1. Import it on self-hosted n8n or n8n Cloud (workflow menu → Import
   from file). The first version should start from a Manual Trigger.
   Do not add a Schedule trigger in that first export.
2. HTTP Request nodes fetch four raw files, pinned to a commit SHA
   rather than floating `main`:
   - `data/synthetic/ehr_sample.csv`
   - `data/synthetic/omop_sample/CONDITION_OCCURRENCE.csv`
   - `data/synthetic/omop_sample/DRUG_EXPOSURE.csv`
   - `data/synthetic/fhir_bundle_sample.json`
   URL pattern:
   `https://raw.githubusercontent.com/developer-rpai/sidha/<sha>/<path>`.
   The tree these notes were written against is `main` at
   `7d73ee824910969f27ea9c545de9200e7794bebd`.
3. A Code node applies only the checks in
   [expected-shape.md](expected-shape.md).
4. The summary item has keys `workflow`, `git_sha`, `generated_at`,
   `status` (`pass` or `fail`), and `checks` (name, `pass` boolean,
   `detail` string). `status` is `fail` if a required header or
   `resourceType` check fails. A missing date is a skip, listed in
   `detail`, and does not by itself fail the run, because the committed
   bundle already has one dateless Condition.
5. Default output is the n8n execution item. An optional HTTP Request
   node may post that summary, but only if the operator pastes their own
   URL into an empty parameter named `SIDHA_SUMMARY_WEBHOOK_URL`, and
   that node ships disabled. Do not hard-code Slack, email, or a GitHub
   issue comment. Do not attach raw fixture bodies.

No pass rate, row-count target, or timing target is part of the design.
The first real summary is whatever the first n8n execution prints.
Do not paste a fabricated pass/fail into this file to make the note
look finished.

## Not in this commit

- The n8n JSON export
- `tests/test_expected_shape.py`
- Any live call to Reddit or a clinical API
