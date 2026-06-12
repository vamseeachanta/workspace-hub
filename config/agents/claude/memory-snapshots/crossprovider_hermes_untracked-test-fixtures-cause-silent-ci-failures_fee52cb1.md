---
name: crossprovider hermes untracked-test-fixtures-cause-silent-ci-failures
description: Untracked test fixtures cause silent CI failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-fixtures, ci-drift, git-tracking]
---

Tests passing locally with untracked fixture/implementation-notes files means CI checkout fails when those files don't exist. If tests depend on untracked files, they must be added to version control or tests will pass in worktree but fail in CI. Check `git status` for untracked test dependencies before approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
