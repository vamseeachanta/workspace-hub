---
name: crossprovider codex concurrent-git-worktree-mutations-race-on-lock
description: Concurrent git worktree mutations race on lock
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [git, concurrency, worktree, threading]
---

Multiple threads calling git worktree add/remove simultaneously race the repo's worktree/index lock → one fails with exit 255. Wrap both add_worktree() and remove_worktree() in a module-level threading.Lock(), with 3-attempt backoff for transient failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
