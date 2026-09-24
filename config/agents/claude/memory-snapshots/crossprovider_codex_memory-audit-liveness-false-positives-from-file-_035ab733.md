---
name: crossprovider codex memory-audit-liveness-false-positives-from-file-
description: Memory-audit liveness false positives from file-freshness masking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [memory-systems, monitoring, false-positives]
---

If a memory bridge fails silently (e.g., runs in dry-run, no heartbeat), audit checks that only verify file age report MEMORY-FRESH even when publication is broken. Heartbeat and publication state must be checked independently of file modification times.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
