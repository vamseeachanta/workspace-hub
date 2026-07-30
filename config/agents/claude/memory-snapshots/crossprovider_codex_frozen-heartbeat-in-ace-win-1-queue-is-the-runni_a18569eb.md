---
name: crossprovider codex frozen-heartbeat-in-ace-win-1-queue-is-the-runni
description: Frozen heartbeat in ace-win-1 queue is the running-state signal
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [licensed-runs, ace-win-1, heartbeat, monitoring]
---

When ace-win-1 heartbeat timestamp stops advancing, a licensed run is actively executing. Do not interpret frozen heartbeat as timeout/failure. Retry windows (e.g., 3h after claim for OrcaWave viscous runs) remain valid even with a stale heartbeat timestamp.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
