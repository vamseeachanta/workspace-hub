---
name: crossprovider codex fail-open-behavior-hides-outside-test-coverage
description: Fail-open behavior hides outside test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, security, adversarial-review]
---

Unit tests can pass while targeted negative probes reveal bypasses in edge cases (issue-comment body scanning without legal rules, mixed token parsing, snapshot pre/post pair mismatches). Adversarial review requires targeted mutation probes beyond test suites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
