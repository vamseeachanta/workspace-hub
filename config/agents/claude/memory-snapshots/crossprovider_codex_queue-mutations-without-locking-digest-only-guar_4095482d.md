---
name: crossprovider codex queue-mutations-without-locking-digest-only-guar
description: Queue mutations without locking: digest-only guards are race-prone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency-hazard, race-condition, data-integrity]
---

Using only digest snapshots and assertions to guard multi-writer queue operations is race-prone. Two writers can snapshot the same digest, both pass assertions, then last-write-wins silently corrupts shared state. True mutual exclusion (locking/claiming) is needed for correctness in concurrent scenarios.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
