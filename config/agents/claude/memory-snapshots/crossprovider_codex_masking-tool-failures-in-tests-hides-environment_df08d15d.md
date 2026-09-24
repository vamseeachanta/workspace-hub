---
name: crossprovider codex masking-tool-failures-in-tests-hides-environment
description: Masking tool failures in tests hides environment-specific bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, ci-cd, environment-specificity, regression-coverage]
---

Test suites that pass locally may silently fail in constrained environments (CI, sandbox, container) when error paths are masked (e.g., `uv` or Python calls wrapped with `|| echo 0`). If a test passes in one environment but the underlying tool fails in another, the test coverage is illusory. Ensure tests either run the actual tool with real error propagation or explicitly mock the constraint being tested.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
