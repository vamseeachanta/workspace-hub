---
name: crossprovider codex structured-proof-validation-must-check-shape-typ
description: Structured proof validation must check shape, type, and cross-field consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, testing, proof-structure, invariants]
---

Validating structured evidence (probe records, configuration blocks) by checking only presence or truthiness misses critical invariants. Validation must check exact shape, field types, cardinality, and relationships between fields. Test naming should expose the specific invariant being verified (e.g., 'malformed entry shape rejected') not just pass/fail outcomes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
