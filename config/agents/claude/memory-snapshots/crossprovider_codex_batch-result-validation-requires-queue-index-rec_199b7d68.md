---
name: crossprovider codex batch-result-validation-requires-queue-index-rec
description: Batch result validation requires queue-index reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [batch-validation, data-integrity, quality-gates]
---

Validating batch transitions (accepted, rejected, target counts) against actual artifact inventory is critical; per-row scoring alone misses pre-existing duplicates and malformed entries. Row-count arithmetic catches data-integrity issues that item-level verdicts ignore.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
