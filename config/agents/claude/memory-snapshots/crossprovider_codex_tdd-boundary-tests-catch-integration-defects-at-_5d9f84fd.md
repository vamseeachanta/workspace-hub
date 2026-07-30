---
name: crossprovider codex tdd-boundary-tests-catch-integration-defects-at-
description: TDD boundary tests catch integration defects at file divisions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [tdd, integration-testing]
---

Strict RED-GREEN-REFACTOR at file boundaries (write test, observe failure, implement, observe pass) exposes integration gaps that diff reviews miss. When a scheduler test expects behavior from the reporter module, the scheduler owns the integration test at its boundary, not the reporter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
