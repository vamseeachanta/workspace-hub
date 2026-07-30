---
name: crossprovider codex isolated-worktrees-after-merge-prevent-parallel-
description: Isolated worktrees after merge prevent parallel-session conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git-workflow, worktree, concurrency]
---

After merging a branch, create isolated implementation worktrees without touching other parallel sessions' checkouts. Fetch only the target ref to local DB; avoid operations that stall on other branches or mutate shared state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
