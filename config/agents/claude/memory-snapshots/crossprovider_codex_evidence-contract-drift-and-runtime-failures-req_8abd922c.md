---
name: crossprovider codex evidence-contract-drift-and-runtime-failures-req
description: Evidence-contract drift and runtime failures require distinct classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, monitoring, contracts]
---

Cron-health monitoring must explicitly separate 'task output at wrong path' (contract mismatch) from 'task failed before producing output' (runtime failure). Current pattern-grep approaches conflate these.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
