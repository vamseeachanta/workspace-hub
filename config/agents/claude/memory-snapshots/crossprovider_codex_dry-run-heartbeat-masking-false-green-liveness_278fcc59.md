---
name: crossprovider codex dry-run-heartbeat-masking-false-green-liveness
description: Dry-run heartbeat masking false-green liveness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduling, observability, automation-hazard]
---

Scheduled tasks running in dry-run mode can mask missing actual heartbeats—the last-run timestamp updates but the critical automation doesn't execute. Check heartbeat signals independently from cron timestamps to catch false-green liveness signals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
