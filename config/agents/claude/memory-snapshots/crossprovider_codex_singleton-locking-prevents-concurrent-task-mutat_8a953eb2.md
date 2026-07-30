---
name: crossprovider codex singleton-locking-prevents-concurrent-task-mutat
description: Singleton locking prevents concurrent task mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [concurrency, locking, operations]
---

Overlapping same-task cron runs indicate missing singleton locks, distinct from just detecting long-running jobs. Critical for mutation-bearing tasks to prevent concurrent writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
