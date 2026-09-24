---
name: crossprovider gemini column-candidate-selection-pattern-for-variable-
description: Column-candidate selection pattern for variable schemas
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-ingest, schema-variability, pattern]
---

When working with government datasets (BSEE, OSHA, etc.) that may have multiple column names for the same semantic field, use a `_pick_col(df, ['candidate1', 'candidate2', ...])` helper to gracefully select the first available. This avoids hard-coding schema assumptions and makes adapters portable across data sources.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
