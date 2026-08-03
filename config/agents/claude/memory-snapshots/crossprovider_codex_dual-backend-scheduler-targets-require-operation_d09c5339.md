---
name: crossprovider codex dual-backend-scheduler-targets-require-operation
description: Dual-backend scheduler targets require operation-level representation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [architecture, scheduling]
---

Crontab and systemd (or Windows Task Scheduler) cannot be distinguished at path scope. Registry must represent scheduler targets at operation level with completeness attestation to avoid silently dropping mutations for one backend.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
