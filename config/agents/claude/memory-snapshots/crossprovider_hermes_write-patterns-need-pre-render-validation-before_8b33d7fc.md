---
name: crossprovider hermes write-patterns-need-pre-render-validation-before
description: Write patterns need pre-render validation before atomic writes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [write-patterns, transactionality, dry-run-safety]
---

In promoter/coordinator patterns, rendering and validating all outputs (scaffolds, CSVs, etc.) must complete BEFORE any write_atomic call. Late validation failures mid-write cause partial writes. Even in dry-run, all paths must be validated first so that failure is clean. Solution: collect+validate+render all before touching disk.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
