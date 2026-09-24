---
name: crossprovider codex concurrent-file-modification-requires-locking-an
description: Concurrent file modification requires locking and compare-and-swap
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, file-transactions, crontab-safety]
---

If external tools modify the same crontab while a transaction runs, backup+rollback is insufficient. Require flock acquisition + read-before-write compare-and-swap: read, compute, re-read before install, abort if changed. Use shared locks if external tool can honor them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
