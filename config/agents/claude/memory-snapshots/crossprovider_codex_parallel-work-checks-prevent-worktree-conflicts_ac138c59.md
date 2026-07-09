---
name: crossprovider codex parallel-work-checks-prevent-worktree-conflicts
description: Parallel-work checks prevent worktree conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [concurrency-awareness, pre-execution-checks, worktree-safety]
---

Before creating a worktree or scheduling an isolated run, check for parallel processes, open PRs, and active branches. Concurrent modifications to the same repo can deadlock or corrupt shared state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
