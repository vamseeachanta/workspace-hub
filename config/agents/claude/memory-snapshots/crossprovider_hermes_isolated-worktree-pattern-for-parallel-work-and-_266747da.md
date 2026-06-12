---
name: crossprovider hermes isolated-worktree-pattern-for-parallel-work-and-
description: Isolated worktree pattern for parallel work and merges
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-patterns, worktrees, parallel-work, safety]
---

Use isolated worktrees under `/mnt/local-analysis/worktrees/...` for edits, merges, and implementation work rather than modifying the main checkout directly. Avoids lock-race conditions and allows parallel agent lanes without conflicting git state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
