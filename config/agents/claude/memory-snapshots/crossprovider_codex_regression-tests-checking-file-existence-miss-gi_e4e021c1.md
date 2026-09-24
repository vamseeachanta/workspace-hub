---
name: crossprovider codex regression-tests-checking-file-existence-miss-gi
description: Regression tests checking file existence miss git staging issues
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git-staging, regression-tests]
---

A test using `(path).exists()` on the filesystem passes for untracked files, missing the actual git staging error. Regression tests for staging correctness must use `git ls-files` to assert tracked status, not filesystem existence checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
