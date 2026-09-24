---
name: crossprovider codex incomplete-source-data-requires-explicit-scope-d
description: Incomplete source data requires explicit scope definition in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, source-coverage, scope-definition]
---

When a data source is incomplete (e.g., CORES has production volumes but not crude density), the plan must explicitly define whether the outcome is 'partial feature with named gaps' or 'all-or-nothing with fallback to legacy defaults'. Silent fallback to defaults masks the incompleteness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
