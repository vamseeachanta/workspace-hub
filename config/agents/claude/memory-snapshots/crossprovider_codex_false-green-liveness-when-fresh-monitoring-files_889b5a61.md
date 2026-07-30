---
name: crossprovider codex false-green-liveness-when-fresh-monitoring-files
description: False-green liveness when fresh monitoring files mask missing heartbeats
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [monitoring, gotcha, ecosystem-tooling]
---

Scheduler/bridge systems can report spurious freshness if monitoring outputs (e.g., Hermes files) exist but the actual heartbeat signal is missing. Regular audits must verify both file recency AND bridge execution, not just file timestamps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
