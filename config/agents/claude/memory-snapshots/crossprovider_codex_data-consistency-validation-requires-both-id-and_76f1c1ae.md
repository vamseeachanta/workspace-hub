---
name: crossprovider codex data-consistency-validation-requires-both-id-and
description: Data consistency validation requires both ID and field-level matching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, consistency-checking, multi-artifact-sync]
---

When validating that multiple data artifacts (e.g., JSON report + JSONL ledger) are in sync, matching only by ID or key fields will miss field-level drift. Require full normalized equality across all fields after sorting by the primary key. This caught mismatches in O&G disposition report/ledger validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
