---
name: crossprovider codex test-passing-does-not-imply-plan-coverage
description: Test passing does not imply plan coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, test-coverage, adversarial-review]
---

Unit test suites can green while plan-required RED checks (raw-source non-access, marker-collision regression, tracked-file validation, prior-batch regression) remain unimplemented. Adversarial reviews must cross-check test output against the approved plan's RED list explicitly; test pass is necessary but not sufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
