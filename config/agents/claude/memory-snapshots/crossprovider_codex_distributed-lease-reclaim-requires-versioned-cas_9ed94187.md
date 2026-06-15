---
name: crossprovider codex distributed-lease-reclaim-requires-versioned-cas
description: Distributed lease reclaim requires versioned CAS with fencing to prevent double-execution
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [distributed-systems, concurrency, coordination]
---

Treating 'stale past TTL' as reclaimable without atomic compare-and-swap allows two coordinators to both claim the lease and execute concurrently. Requires versioned refresh/reclaim semantics, mid-run liveness verification with fencing tokens, and atomic state transitions to prevent race conditions under clock skew and network partitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
