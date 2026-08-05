---
name: crossprovider codex tdd-tests-must-embed-literal-expected-values-nev
description: TDD tests must embed literal expected values, never inferred thresholds
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [testing, tdd, regression-testing]
---

Test cases should assert exact, hardcoded expected values rather than computed thresholds. Inferred thresholds or range checks permit broken implementations to pass. Include explicit failure modes and reasons for each test case.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
