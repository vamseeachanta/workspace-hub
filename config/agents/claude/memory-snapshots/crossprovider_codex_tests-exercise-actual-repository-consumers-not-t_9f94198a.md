---
name: crossprovider codex tests-exercise-actual-repository-consumers-not-t
description: Tests exercise actual repository consumers, not test-local reference implementations
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, tdd, consumer-verification]
---

Tests that define validation logic inside the test module won't catch defects in missing or broken Task N consumers. Validators and authorizers must be real repository modules that tests import and exercise, not reimplemented as fixtures. Declarative config flags don't establish behavior—tests must verify actual code paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
