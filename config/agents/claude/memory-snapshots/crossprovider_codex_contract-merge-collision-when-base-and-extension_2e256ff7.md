---
name: crossprovider codex contract-merge-collision-when-base-and-extension
description: Contract merge collision when base and extension redefine the same identity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-composition, schema-merge, specification-gap]
---

When a v3 contract extension redeclares a v1 base handoff (same from/to/condition) with additional fields, the stated merge rule (append uniquely) cannot preserve both field sets. The key is not unique across versions; deduplication discards either base or v3 fields. Merge-by-identity must define field-union semantics or replace conflicts explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
