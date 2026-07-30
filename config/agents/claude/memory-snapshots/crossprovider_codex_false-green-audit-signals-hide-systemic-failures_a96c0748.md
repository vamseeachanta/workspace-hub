---
name: crossprovider codex false-green-audit-signals-hide-systemic-failures
description: False-green audit signals hide systemic failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [observability, audit-health, false-positives]
---

Fresh artifacts can mask stale state (e.g., recent Hermes snapshots masking missing heartbeat cron). A freshness audit returning green does not verify the underlying signal (scheduler health, bridge execution). Verify signal sources independently and separately from data freshness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
