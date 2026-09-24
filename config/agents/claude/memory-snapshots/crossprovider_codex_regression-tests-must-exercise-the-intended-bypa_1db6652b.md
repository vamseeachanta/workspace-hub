---
name: crossprovider codex regression-tests-must-exercise-the-intended-bypa
description: Regression tests must exercise the intended bypass scenario
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, regression-coverage, adversarial-testing]
---

A test that leaves discriminators or integrity checks intact while tampering with outputs can miss coherent-tampering pathways. Regression tests should include the exact bypass the fix was intended to close (e.g., mutable-path downgrade, hash recomputation, field changes).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
