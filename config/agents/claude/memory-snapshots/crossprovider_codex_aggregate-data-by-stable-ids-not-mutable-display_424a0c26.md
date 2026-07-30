---
name: crossprovider codex aggregate-data-by-stable-ids-not-mutable-display
description: Aggregate data by stable IDs, not mutable display names
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [aggregation, data-modeling, identifiers]
---

Grouping on name fields (field_name, operator_name) splits real entities when spellings vary or names change. Use stable identifiers (numbers, UUIDs) as aggregation keys, then select display names deterministically after grouping (latest nonblank, most frequent, or lexical tie-break).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
