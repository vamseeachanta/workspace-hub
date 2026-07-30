---
name: crossprovider codex frozen-heartbeat-is-documented-running-signature
description: Frozen heartbeat is documented running signature for serialized licensed runs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [monitoring, licensed-compute, queue-dispatch]
---

In serialized-seat licensed-run queues, heartbeat stasis (not change) signals a job is in flight. Monitor state at predictable intervals (e.g., ~3h for 3-hour jobs) rather than on heartbeat update. Treat heartbeat freeze as healthy; investigate only if heartbeat is missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
