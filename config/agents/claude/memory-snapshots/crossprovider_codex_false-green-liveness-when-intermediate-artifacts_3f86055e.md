---
name: crossprovider codex false-green-liveness-when-intermediate-artifacts
description: False-green liveness when intermediate artifacts mask missing critical signals
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [monitoring, liveness-signals, auditing]
---

Fresh generated files (e.g., Hermes memory entries) can cause monitoring to report MEMORY-FRESH even when critical background work is missing (e.g., bridge heartbeat). Freshness depends on both source and prerequisite signals, not just artifact timestamps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
