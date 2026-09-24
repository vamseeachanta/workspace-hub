---
name: crossprovider codex tdd-gate-requires-behavior-regression-tests-not-
description: TDD gate requires behavior regression tests, not inventory checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, testing, approval-gate]
---

Mandatory TDD gate requires actual pre-change regression tests for runtime code being modified. Inventory checks, documentation assertions, and process validations do not satisfy TDD. If implementation touches Python modules or changes runtime behavior, add behavior-preservation tests before the implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
