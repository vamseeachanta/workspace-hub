---
name: crossprovider codex liveness-signals-from-cached-artifacts-can-be-fa
description: Liveness signals from cached artifacts can be false-positive
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [infrastructure, monitoring, caching, health-checks]
---

Fresh file timestamps (e.g., `MEMORY-FRESH` on recent Hermes files) don't prove daemon or bridge health. A stale cron job still created fresh marker files while publication was disabled. Require heartbeat checks or explicit timestamp validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
