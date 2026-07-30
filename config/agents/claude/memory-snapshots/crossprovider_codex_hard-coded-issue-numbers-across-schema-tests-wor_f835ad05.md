---
name: crossprovider codex hard-coded-issue-numbers-across-schema-tests-wor
description: Hard-coded issue numbers across schema/tests/workflows create brittle coupling
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [schema-design, coupling, maintainability]
---

When issue dependencies change (e.g., #69 from #68 → #65), the ID repeats across schema, validator, tests, and workflows. Centralizing in schema and deriving via functions prevents missed updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
