---
name: crossprovider codex semantic-validation-requires-cross-field-consist
description: Semantic validation requires cross-field consistency checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [schema-validation, semantic-consistency, data-quality]
---

Structured data with multiple enumerated fields needs validation of field combinations, not just individual values. Contradictory combinations (e.g., `value_basis='point'` with `bound_type='closed_range'`) must be rejected by schema.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
