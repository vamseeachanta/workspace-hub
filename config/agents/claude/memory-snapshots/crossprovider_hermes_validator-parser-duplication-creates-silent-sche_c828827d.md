---
name: crossprovider hermes validator-parser-duplication-creates-silent-sche
description: Validator/parser duplication creates silent schema drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, maintainability, schema, anti-pattern]
---

When the same schema is implemented in two places (submit-batch.sh inline YAML parsing + validate_manifest.py), they diverge silently: submit-batch accepts cases validator rejects (empty jobs, wrong case for solver_type) and ignores others (schema_version). A manifest can pass preflight but fail submission. Reuse validators directly instead of duplicating them.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
