---
name: crossprovider codex nested-validation-requires-correct-object-scope
description: Nested validation requires correct object scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, nested-data, scope-confusion]
---

When validating fields within nested structures, ensure the validator receives the complete parent record, not just the nested field. Passing only `noncompatible_pair` instead of the root `record` to reconciliation-ref validation causes checks to examine the wrong object scope and miss invalid refs on compatible-only records.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
