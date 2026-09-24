---
name: crossprovider codex false-green-liveness-signals-from-stale-heartbea
description: False-green liveness signals from stale heartbeat masks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, liveness-signals, audit-integrity]
---

Freshness audits can report HEALTHY when fresh files from one subsystem mask missing heartbeats from critical infrastructure (e.g., dry-run bridge runs). Require explicit heartbeat/liveness verification independent of artifact freshness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
