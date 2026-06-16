---
name: crossprovider codex registered-git-worktrees-persist-outside-coordin
description: Registered Git worktrees persist outside coordination directories
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [worktree, cleanup, git-state]
---

A coordination directory like `/mnt/local-analysis/worktrees/` can be empty while actual worktrees exist at their registered paths (e.g., `/tmp/wt-*`, `.claude/worktrees/agent-*`). Worktrees are registered in `.git/worktrees/` and survive directory moves. Always use `git worktree list` and `git worktree remove` to clean up; deleting the physical directory leaves a stale registration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
