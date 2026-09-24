---
name: crossprovider codex data-normalization-schemas-require-explicit-iden
description: Data normalization schemas require explicit identity and field-mapping contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-schema, plan-review, normalization, correctness]
---

When plans involve multiple data sources with normalization or deduplication, they must specify identity join contracts (including bare vs canonical form handling), per-source field mappings, domain attribution rules, and cross-source deduplication semantics. Unspecified transformations (e.g., bare 64-hex to sha256) and missing supplemental source schemas are recurring high-signal defects that block approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
