---
name: crossprovider hermes stale-worktree-cleanup-requires-dual-scan-git-wo
description: Stale worktree cleanup requires dual scan: git worktree list + filesystem orphan walk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-cleanup, git-hygiene, orphaned-files]
---

Checking only `git worktree list` misses hundreds of MB of orphaned directories in `.claude/worktrees/`. Must scan both the registered worktree list AND the filesystem `.claude/worktrees/` directory for broken `.git` pointer files and unregistered worktree roots.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
