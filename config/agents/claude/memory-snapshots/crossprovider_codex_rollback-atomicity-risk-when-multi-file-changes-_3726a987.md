---
name: crossprovider codex rollback-atomicity-risk-when-multi-file-changes-
description: Rollback atomicity risk when multi-file changes land as merge commit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [rollback, git, deployment]
---

Plans proposing `git revert <merge-commit>` for rollback may face issues if the PR contains many individual file changes; single revert may not be atomic for partial rollback scenarios. Verify merge shape and rollback constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
