---
name: crossprovider codex advisory-locking-opens-race-window-on-write-veri
description: Advisory locking opens race window on write-verify-rollback
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [concurrency, file-consensus, rollback-safety]
---

Releasing a lock before post-write verification allows concurrent modifications to slip in undetected. On rollback, the stale snapshot overwrites the external writer's changes without CAS comparison. Either hold lock through verification, or use CAS refusal instead of advisory locks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
