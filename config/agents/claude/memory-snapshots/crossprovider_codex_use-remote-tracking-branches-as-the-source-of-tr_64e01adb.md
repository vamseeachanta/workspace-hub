---
name: crossprovider codex use-remote-tracking-branches-as-the-source-of-tr
description: Use remote-tracking branches as the source of truth in multi-worktree workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git, workflow, collaboration]
---

Local branch heads can lag behind their remotes due to incomplete fetches or local resets. Always reference `origin/main` or the remote branch when synchronizing across worktrees or checking for uncommitted changes. Use `git fetch` to refresh remote state before making synchronization decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
