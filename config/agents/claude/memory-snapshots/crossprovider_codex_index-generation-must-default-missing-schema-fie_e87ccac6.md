---
name: crossprovider codex index-generation-must-default-missing-schema-fie
description: Index generation must default missing schema fields for archived records
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-evolution, index-generation, backward-compatibility]
---

When adding a new column to a generated index, the generator must provide defaults for missing values in historical records predating the schema change. Bulk backfills often touch only active items, breaking index generation for archived records.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
