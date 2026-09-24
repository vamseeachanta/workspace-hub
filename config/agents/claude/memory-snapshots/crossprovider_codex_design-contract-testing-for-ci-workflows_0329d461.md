---
name: crossprovider codex design-contract-testing-for-ci-workflows
description: Design contract testing for CI workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-cd, testing, workflow]
---

Test CI workflow behavior (reporting assertions, footprint measurements, conditional dispatch) using pytest + workflow contract tests rather than relying solely on schema linting. Catches runtime mismatches that schema validators like `actionlint` may miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
