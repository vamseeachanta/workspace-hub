---
name: crossprovider hermes large-repo-worktree-materialization-times-out-un
description: Large repo worktree materialization times out under parallel I/O load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktree, performance, parallel-agents, large-repo]
---

workspace-hub 33K files: worktree checkout takes 17min–1h+ depending on parallel-agent I/O contention. Parallel agent isolation via worktrees is too expensive. Prefer serial commit agents (write files only; main session commits) or use GIT_INDEX_FILE snapshot pattern to avoid worktree overhead.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
