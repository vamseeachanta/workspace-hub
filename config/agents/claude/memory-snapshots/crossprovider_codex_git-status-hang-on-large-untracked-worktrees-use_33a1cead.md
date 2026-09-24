---
name: crossprovider codex git-status-hang-on-large-untracked-worktrees-use
description: Git-status hang on large untracked worktrees—use bounded checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-ops, workspace-hub, performance]
---

When auditing large repos (workspace-hub ~33K files), `git status -uall` times out scanning untracked trees. Fallback pattern: `git diff --quiet` + `git diff --cached --quiet` + `git worktree list --porcelain` + `git branch --merged` avoid full untracked enumeration and complete reliably.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
