---
name: crossprovider gemini concurrent-safe-state-mutations-with-explicit-lo
description: Concurrent-safe state mutations with explicit locking
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [locking, concurrency, state-mutations]
---

Acquire both a repo-based lockfile (in `<repo>/.locks/`, not `/tmp`) and `fcntl.LOCK_EX` on the target file before appending state. This ensures race-free batch sweep operations in concurrent environments.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
