---
name: crossprovider codex memory-bridge-liveness-produces-false-positive-w
description: Memory bridge liveness produces false-positive when running dry-run
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [memory-system, monitoring-hazard, dry-run-gotcha]
---

Dry-run bridge execution leaves no heartbeat/completion record, yet fresh Hermes files cause `MEMORY-FRESH` audit to report false-green liveness. Monitor must verify heartbeat/bridge completion independently, not infer from output freshness. Affects cross-provider session reconciliation reliability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
