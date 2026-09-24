---
name: crossprovider codex test-budgets-must-account-for-actual-matrix-scop
description: Test budgets must account for actual matrix scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, estimation, scope]
---

When specifying a test suite matrix (normal repo, linked worktrees, existing/missing/non-executable states, etc.), calculate the realistic line count needed per test case, not just total lines. Aspirational budgets that compress test coverage to fit a target break the verification contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
