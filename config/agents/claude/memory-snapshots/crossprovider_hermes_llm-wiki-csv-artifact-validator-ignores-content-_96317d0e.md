---
name: crossprovider hermes llm-wiki-csv-artifact-validator-ignores-content-
description: llm-wiki CSV artifact validator ignores content—only checks existence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, validation-gap, contract-enforcement, defect]
---

Validator does not parse CSV files, never schema-checks or validates row counts vs JSONL. Malformed CSVs pass validation. Add CSV parsing, header validation, row-count cross-checks, and explicit failure on malformed content.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
