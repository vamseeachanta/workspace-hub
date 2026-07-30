---
name: crossprovider codex memory-system-false-green-heartbeat-signals
description: Memory system false-green heartbeat signals
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [memory-system, monitoring, liveness]
---

Fresh artifact timestamps mask missing bridge heartbeats, creating false MEMORY-FRESH status when liveness is broken. Verify active heartbeat explicitly, not artifact freshness; stale cron state silently breaks circulation while appearing healthy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
