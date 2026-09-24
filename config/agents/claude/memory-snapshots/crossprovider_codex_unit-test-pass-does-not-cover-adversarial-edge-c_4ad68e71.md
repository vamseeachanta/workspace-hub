---
name: crossprovider codex unit-test-pass-does-not-cover-adversarial-edge-c
description: Unit test pass does not cover adversarial edge cases; probe with temp fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-sufficiency, edge-case-testing, adversarial-probing]
---

Focused pytest suite passed while adversarial probes against throwaway YAML fixtures (conditional required fields, malformed duplicate doc_key) exposed contract gaps. Integration tests on live repo paths also race with parallel modifications. Fix: unit tests cover happy path; adversarial suite must probe edge cases (duplicates, malformed values, boundary conditions) separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
