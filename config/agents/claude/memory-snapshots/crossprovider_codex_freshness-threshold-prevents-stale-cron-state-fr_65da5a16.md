---
name: crossprovider codex freshness-threshold-prevents-stale-cron-state-fr
description: Freshness threshold prevents stale cron state from masking current health
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [observability, cron, timing]
---

Before copying task statuses from cron-health state, enforce a freshness threshold (36h suggested) to prevent outdated observations from being misinterpreted as current health. Stale state indicates the monitoring job itself may be failing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
