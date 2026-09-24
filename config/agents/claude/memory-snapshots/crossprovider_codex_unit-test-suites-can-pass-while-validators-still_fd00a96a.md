---
name: crossprovider codex unit-test-suites-can-pass-while-validators-still
description: Unit test suites can pass while validators still accept invalid inputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validator-validation, edge-cases]
---

Committed test fixtures may not cover all edge cases and negation patterns. Adversarial mutation probes (e.g., injecting negated assertions into validation clauses) reveal bypasses that pass the test suite. Supplement unit tests with targeted edge-case mutations to verify contract enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
