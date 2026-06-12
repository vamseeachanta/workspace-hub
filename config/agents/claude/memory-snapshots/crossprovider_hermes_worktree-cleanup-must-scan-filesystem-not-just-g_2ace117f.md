---
name: crossprovider hermes worktree-cleanup-must-scan-filesystem-not-just-g
description: Worktree cleanup must scan filesystem, not just git worktree list
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-hygiene, cleanup-debt, filesystem-state]
---

Running `git worktree list` alone misses orphaned directories in `.claude/worktrees/` and sibling paths; can hide hundreds of MB of stale data. Closeout recovery must scan both `git worktree list` and the filesystem under `.claude/worktrees/` and equivalent agent-log paths for broken `.git` pointer files before declaring cleanup complete.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
