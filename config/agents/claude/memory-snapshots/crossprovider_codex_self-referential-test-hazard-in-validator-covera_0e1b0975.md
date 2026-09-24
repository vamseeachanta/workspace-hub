---
name: crossprovider codex self-referential-test-hazard-in-validator-covera
description: Self-referential test hazard in validator coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, validation-gaps, execution-risk]
---

Tests comparing generated output to module constants (e.g., `validate_schema_row()` against `DISALLOWED_FIELDS`) can pass even when required validators are dropped. If a constraint moves from constant AND validator, the test still passes. Require independent fixtures/assertions that prove negative cases without circular reference to implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
