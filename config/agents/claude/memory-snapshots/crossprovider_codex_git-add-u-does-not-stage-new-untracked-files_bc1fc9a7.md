---
name: crossprovider codex git-add-u-does-not-stage-new-untracked-files
description: git add -u does not stage new untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [git, staging, testing]
---

`git add -u` only stages tracked files; new files (even if already in `git diff HEAD` in an uncommitted state) must use explicit `git add <file>` or they'll be omitted from the commit. This is especially important for new test files that provide coverage for implementation changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
