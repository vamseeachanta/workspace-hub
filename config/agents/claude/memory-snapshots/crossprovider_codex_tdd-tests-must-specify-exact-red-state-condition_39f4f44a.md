---
name: crossprovider codex tdd-tests-must-specify-exact-red-state-condition
description: TDD tests must specify exact red-state conditions and expected values before green implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, test-design, red-state, falsifiability]
---

Vacuous tests (testing existing behavior, asserting green without proving red, permitting broken implementations) are worse than no tests. Each test case needs an observable, literal, exact outcome — exact exception messages, exact thresholds, exact fixture data. Include the RED output in commit messages to prove the defect existed before the fix. A test written after the fix is not TDD.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
