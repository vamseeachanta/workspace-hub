---
name: crossprovider hermes plan-acceptance-criteria-must-align-with-tdd-and
description: Plan acceptance criteria must align with TDD and Files-to-Change schema
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-validation, schema, ci-integration]
---

#2665 acceptance criteria required tests/analysis/test_continuous_planning_pipeline.py, but this file was not listed in the TDD section or Files-to-Change table. CI and plan validators cannot infer test scope when acceptance references undeclared tests. Pre-commit plan validation should enforce: acceptance-criteria tests ⊆ (declared TDD tests ∪ modified files in scope).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
