---
name: crossprovider codex generated-artifact-schemas-must-use-exact-plan-s
description: Generated artifact schemas must use exact plan-specified field names
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [generated-artifacts, schema-validation, plan-driven-development]
---

Implemented `standard_status` field instead of approved plan's `regulatory_status`. Approximate naming makes field validation fail silently in tests. Generated schemas must match plan field names exactly, not by semantic equivalence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
