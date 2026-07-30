---
name: crossprovider codex false-green-liveness-signals-from-fresh-auxiliar
description: False-green liveness signals from fresh auxiliary files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [monitoring, liveness, observability]
---

Fresh audit/heartbeat files can mask missing lifecycle events. An audit reporting MEMORY-FRESH while the bridge heartbeat is missing is a false-green. Liveness checks must verify the actual signal (heartbeat, cron output), not the recency of audit artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
