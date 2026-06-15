---
name: crossprovider codex gating-cron-operations-on-optional-resources-wit
description: Gating cron operations on optional resources without absence monitoring creates fleet-wide silent stops
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [distributed-systems, monitoring, operational-safety]
---

A cron that checks 'holds_resource()' and no-ops when false will silently stop fleet-wide if the resource is never acquired, with no alerting. Requires independent 'no valid holder + stale SLA window' detection and alert, not just conditional execution based on resource availability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
