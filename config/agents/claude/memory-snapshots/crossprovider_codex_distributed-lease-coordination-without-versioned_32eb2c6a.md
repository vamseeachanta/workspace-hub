---
name: crossprovider codex distributed-lease-coordination-without-versioned
description: Distributed lease coordination without versioned CAS and fencing enables double-execution and split-brain
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-systems, coordination, lease-hazard]
---

TTL-based lease reclaim without atomic compare-and-swap on generation and fencing tokens allows two coordinators to both decide a lease is stale and execute independently. Renewal must be part of work execution, not separate from it. Liveness-driven reclaim during network partitions can steal leases from healthy workers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
