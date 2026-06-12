---
name: crossprovider hermes csv-validation-skips-structural-checks
description: CSV validation skips structural checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, csv, artifact-integrity]
---

Public graph validator validates JSONL and metadata but does NOT check CSV headers/row parity. Corrupted CSV artifacts with misaligned columns/data pass validation. Add CSV structure validation (header presence, row length, type consistency) before marking artifacts as valid.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
