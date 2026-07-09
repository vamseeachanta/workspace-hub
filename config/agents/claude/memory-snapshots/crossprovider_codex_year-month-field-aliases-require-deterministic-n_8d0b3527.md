---
name: crossprovider codex year-month-field-aliases-require-deterministic-n
description: Year/month field aliases require deterministic normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [csv-parsing, normalization, column-mapping]
---

CSV loaders should map multiple column names for the same data (e.g., CYCLE_YEAR + CYCLE_MONTH vs production_date). Normalize to canonical YYYY-MM format before aggregation. Missing alias detection silently produces blank months.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
