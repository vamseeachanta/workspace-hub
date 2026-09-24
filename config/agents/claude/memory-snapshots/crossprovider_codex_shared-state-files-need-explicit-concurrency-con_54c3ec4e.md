---
name: crossprovider codex shared-state-files-need-explicit-concurrency-con
description: Shared state files need explicit concurrency contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, state-management, fault-tolerance]
---

State files consumed by multiple processes/runs (queues, logs, caches) must document locking strategy (fcntl, mutex, etc.), writer identity, idempotency semantics, and crash recovery behavior upfront. Cannot assume single-writer or implicit ordering. Observed in #2017 email-queue state machine v3 revision adding fcntl advisory locks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
