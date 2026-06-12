---
name: crossprovider hermes schema-contract-mismatches-hide-in-validator-tes
description: Schema/contract mismatches hide in validator test gaps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, schema-validation, artifact-integrity]
---

In #77 public-graph validator, schema documents inputs/outputs as 'committed Markdown under wikis/ only' and edges require 'evidence' field, but tests only checked node paths and validator only required JSONL/digest/counts. Result: untracked files got included in 'committed' artifacts, CSV files were never validated, and missing evidence fields passed silently. Tests that only verify documented behavior miss implementation drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
