---
name: crossprovider hermes cron-health-check-must-exclude-self-referential-
description: Cron health check must exclude self-referential logs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, health-checking, logging, pitfall]
---

Health-checking task that scans append-only error logs will flag itself as unhealthy when its own output contains error patterns. Filter by task ID (skip when checking own tid) or scan other tasks' logs only to avoid false-positive loops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
