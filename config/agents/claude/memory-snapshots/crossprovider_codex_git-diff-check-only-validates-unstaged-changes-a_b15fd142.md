---
name: crossprovider codex git-diff-check-only-validates-unstaged-changes-a
description: git diff --check only validates unstaged changes after staging
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, pre-commit, tooling]
---

After `git add`, the bare `git diff --check` command tests only the unstaged working tree, not staged content. Use `git diff --cached --check` to verify staged changes before commit, or run enforcement before staging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
