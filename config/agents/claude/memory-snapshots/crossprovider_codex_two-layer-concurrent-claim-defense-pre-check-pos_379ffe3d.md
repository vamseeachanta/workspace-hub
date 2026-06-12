---
name: crossprovider codex two-layer-concurrent-claim-defense-pre-check-pos
description: Two-layer concurrent claim defense: pre-check + POSIX atomicity
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [concurrency, work-queue, posix-semantics]
---

For filesystem-based work queues, use pre-check (fast-fail if target exists) plus atomic rename(2) to defend against concurrent claim races. Pre-check is the signaling layer; rename is the actual race-breaker. Advisory locks are insufficient because they do not prevent concurrent execution if both sessions reach the claim point before either sees the lock.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
