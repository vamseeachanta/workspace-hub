---
name: crossprovider codex aggregate-tabular-domain-validation-requires-uni
description: Aggregate/tabular domain validation requires uniqueness checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [validation, data-integrity]
---

Checking dimension names and row ordering is not enough; explicitly prevent duplicate `(dimension, value)` cells and validate all values against a closed set (not just presence). Without this, first baselines can contain conflicting/repeated cells that corrupt downstream cross-tab semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
