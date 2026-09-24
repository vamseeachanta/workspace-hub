---
name: crossprovider codex git-hooks-must-resolve-state-via-git-rev-parse-n
description: Git hooks must resolve state via git rev-parse, not filesystem inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktrees, hooks, correctness]
---

Hooks that check for in-progress operations (rebase, cherry-pick, merge) by reading `.git/rebase-merge` or `.git/CHERRY_PICK_HEAD` fail in linked worktrees, where `.git` is a symlink/file pointing to the per-worktree git directory. Use `git rev-parse --git-dir` to get the real path, then check state files relative to that path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
