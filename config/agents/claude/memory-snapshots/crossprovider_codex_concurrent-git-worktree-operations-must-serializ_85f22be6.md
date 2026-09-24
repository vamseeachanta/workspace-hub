---
name: crossprovider codex concurrent-git-worktree-operations-must-serializ
description: Concurrent git worktree operations must serialize
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, threading, concurrency, worktree, bug-pattern]
---

ThreadPoolExecutor calling git worktree add/remove in parallel causes race conditions on the repo's worktree/index lock, failing with exit 255. Wrap both add_worktree() and remove_worktree() with a module-level threading.Lock(); add retry logic (3 attempts, short backoff) on transient failures to self-heal contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
