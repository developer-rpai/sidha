# sidha-fixture-shape-check

Import [`sidha-fixture-shape-check.json`](sidha-fixture-shape-check.json) on self-hosted n8n or n8n Cloud: workflow menu, Import from File, then run the Manual Trigger. There is no Schedule trigger.

Apache-2.0, same as SIDHA. Free to import. This repo does not sell, host, or require an account beyond your own n8n. There is no Warp file. Warp is only one editor you might use to read the JSON. The workflow does not need Warp to run.

## What it checks

Inflammatory-disease fixture shape for the columns and FHIR fields `sidha.ehr` already loads. Hidradenitis suppurativa is the flagship example in some sample codes, not a rule that other diseases fail. This is not an OHDSI DataQualityDashboard run and not full OMOP CDM or FHIR profile conformance. The column and date-field lists are in [expected-shape.md](expected-shape.md).

The four HTTP Request nodes fetch public synthetic files with no token, pinned to commit `7d73ee824910969f27ea9c545de9200e7794bebd`:

- `data/synthetic/ehr_sample.csv`
- `data/synthetic/omop_sample/CONDITION_OCCURRENCE.csv`
- `data/synthetic/omop_sample/DRUG_EXPOSURE.csv`
- `data/synthetic/fhir_bundle_sample.json`

## Summary

The Code node emits one JSON item. Keys: `workflow`, `git_sha`, `generated_at`, `status` (`pass` or `fail`), and `checks` (each has `name`, `pass`, and `detail`). `status` is `fail` if a required header or `resourceType` check fails. A missing date is a skip. Skips are listed in `detail` and do not by themselves fail the run, because the pinned bundle already has one dateless Condition (ICD-10 E66.9).

No n8n execution is stored in this repo. The first real summary is whatever your own run prints. The summary does not include fixture bodies.

## Optional webhook

The node named `SIDHA_SUMMARY_WEBHOOK_URL` is disabled. Its URL is the empty value `{{ $json.SIDHA_SUMMARY_WEBHOOK_URL }}`. Paste your own endpoint into that URL field and enable the node only if you want the summary posted. Do not point it at Slack, email, or GitHub from this export.
