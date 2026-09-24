---
name: crossprovider codex verification-csv-tables-must-have-parse-status-a
description: Verification CSV tables must have parse_status and machine-readable source mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, verification, csv-format, hardened-contract]
---

Tables added to `_verification-queue.csv` must include parse_status (provisional-unverified, raw-unverified), source_page, and table_id columns so verifiers can trace data back to source. Anonymous data rows without code_id, source_pdf, or page reference violate the verification contract and cannot be validated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
