---
name: crossprovider codex memory-freshness-audit-false-green-when-bridge-i
description: Memory freshness audit false-green when bridge is stale
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [memory-system, liveness-signal, audit-correctness]
---

Fresh Hermes files can mask a broken memory bridge: MEMORY-FRESH audit reports healthy even when the bridge ran in dry-run with no heartbeat. This is a critical false-positive in the liveness signal that makes a broken mechanism appear functional.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
