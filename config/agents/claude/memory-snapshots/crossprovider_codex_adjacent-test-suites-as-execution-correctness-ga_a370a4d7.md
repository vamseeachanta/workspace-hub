---
name: crossprovider codex adjacent-test-suites-as-execution-correctness-ga
description: Adjacent test suites as execution correctness gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-scope, regression-gate, shared-infrastructure]
---

When new work touches shared infrastructure (e.g., all-root semantic index #725), existing test suites for prior issues (#731/#732) must remain green as a regression gate. Codex empirically verified this by running adjacent tests; do not assume unrelated tests still pass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
