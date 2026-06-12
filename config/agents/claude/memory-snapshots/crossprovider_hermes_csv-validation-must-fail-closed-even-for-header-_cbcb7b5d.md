---
name: crossprovider hermes csv-validation-must-fail-closed-even-for-header-
description: CSV validation must fail-closed even for header-only files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, csv, testing]
---

When validating CSV output against JSONL row counts, distinguish between successful parse with zero rows versus parse failure. Fail-close if JSONL contains rows but CSV is header-only or missing, even if CSV parsing succeeded. Guard validation checks only by row existence, not by truthiness of empty list.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
