---
name: crossprovider codex licensed-run-state-via-queue-heartbeat-not-ssh-c
description: Licensed-run state via queue heartbeat, not SSH connectivity
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [licensed-runs, heartbeat, state-signal]
---

Frozen ace-win-1 queue heartbeat is the documented running signature for long-running licensed solves. Direct SSH liveness checks can be stale; always verify latest heartbeat timestamp in queue before assuming a host is idle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
