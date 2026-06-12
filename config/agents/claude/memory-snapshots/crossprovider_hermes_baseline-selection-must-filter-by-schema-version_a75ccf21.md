---
name: crossprovider hermes baseline-selection-must-filter-by-schema-version
description: Baseline selection must filter by schema/version
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-migration, schema-evolution, baseline-stability]
---

When computing deltas against a previous artifact baseline, explicitly filter by schema_version or metadata version before selecting 'latest'. Otherwise stale schema versions pollute the delta. Document in code that version filtering is load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
