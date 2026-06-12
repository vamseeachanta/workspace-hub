---
name: crossprovider codex ci-test-suites-fail-silently-when-using-git-diff
description: CI test suites fail silently when using git diff against clean working tree
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ci-cd, testing, testing-strategy]
---

Test suites that select tests via git diff fail in CI environments where the working tree is clean (no staging area). Test selection must be mode-aware (test-all in CI, test-changed locally) or always run the full suite in CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
