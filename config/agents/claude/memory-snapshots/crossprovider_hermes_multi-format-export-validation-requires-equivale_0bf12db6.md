---
name: crossprovider hermes multi-format-export-validation-requires-equivale
description: Multi-format export validation requires equivalence testing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-validation, export-formats, csv, jsonl]
---

When data is exported in multiple formats (CSV, JSONL, etc.), large churn differences in one format vs minimal changes in another can hide synchronization bugs. Add explicit equivalence validation comparing node/edge sets across formats, not just format-level correctness tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
