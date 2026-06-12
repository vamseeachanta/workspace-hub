---
name: crossprovider codex tdd-gates-first-failing-tests-lock-wrapper-behav
description: TDD gates first: failing tests lock wrapper behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tdd, gates, test-first]
---

Before editing a gate script or wrapper, write a failing test that locks the expected invocation contract (CLI flags, dry-run behavior, output format). Fixes the contract in place before implementation. Prevents silent regressions when downstream code assumes the old contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
