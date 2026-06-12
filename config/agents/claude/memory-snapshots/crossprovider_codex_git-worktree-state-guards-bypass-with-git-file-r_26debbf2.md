---
name: crossprovider codex git-worktree-state-guards-bypass-with-git-file-r
description: Git worktree state guards bypass with .git file reference
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-worktree, shell-correctness, hooks, post-commit]
---

Post-commit hooks checking `.git/rebase-merge` or `.git/CHERRY_PICK_HEAD` directly fail in linked worktrees where `.git` is a pointer file. Use `git rev-parse --git-dir` to resolve the real per-worktree git directory before checking state files. Affects auto-push guards and history-rewrite detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
