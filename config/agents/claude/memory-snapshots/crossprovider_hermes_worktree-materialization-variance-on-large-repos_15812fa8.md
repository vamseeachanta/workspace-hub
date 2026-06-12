---
name: crossprovider hermes worktree-materialization-variance-on-large-repos
description: Worktree materialization variance on large repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-performance, worktrees, large-repo]
---

Checkout times for 19K+ file worktrees range 17min–1h+ under parallel I/O; use sanity-poll at 5min to detect stalls. Worktree isolation strategy trades off speed for safety on large monorepos like workspace-hub.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
