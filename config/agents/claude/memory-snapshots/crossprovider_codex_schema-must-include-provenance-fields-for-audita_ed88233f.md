---
name: crossprovider codex schema-must-include-provenance-fields-for-audita
description: Schema must include provenance fields for auditability
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [schema, provenance, auditability]
---

_norms.json with only "generated, config_hash, entries" is insufficient. Add source path/hash, row counts, population IDs, n-per-comparator, aggregation method, excluded counts, status-per-comparator so downstream consumers can verify and reproduce.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
