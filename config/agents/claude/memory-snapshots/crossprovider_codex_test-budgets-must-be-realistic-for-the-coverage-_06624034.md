---
name: crossprovider codex test-budgets-must-be-realistic-for-the-coverage-
description: Test budgets must be realistic for the coverage matrix; aspirational budgets force under-proven tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing, planning, scope-management]
---

A brief requiring ≤400-line tests to cover manifest parsing, two Git modes, malformed inputs, TOCTOU, detection classes, and full worktree matrix across multiple test files is not credible. Do not dispatch with aspirational budgets; either reduce the matrix or expand the file allowance explicitly. Compressed tests hide gaps and skip evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
