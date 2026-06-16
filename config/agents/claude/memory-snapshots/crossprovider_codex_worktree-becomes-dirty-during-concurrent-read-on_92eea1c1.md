---
name: crossprovider codex worktree-becomes-dirty-during-concurrent-read-on
description: Worktree becomes dirty during concurrent read-only operations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [concurrency, worktree, race-condition, synchronization]
---

While running read-only classification tasks (sessions 1-2), the working tree's `HEAD` and dirty set changed mid-scan; background auto-sync or parallel sessions are modifying the tree even when the current task is read-only. Always re-check `git status` before assuming stale state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
