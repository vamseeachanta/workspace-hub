---
name: crossprovider codex memory-bridge-false-green-liveness-signal
description: Memory bridge false-green liveness signal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [memory-system, ecosystem, liveness-detection]
---

Bridge running in dry-run mode causes stale Hermes metadata files to trigger a false `MEMORY-FRESH` signal in the freshness audit, masking missing heartbeat/publication state. Requires explicit heartbeat validation separate from file modification time checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
