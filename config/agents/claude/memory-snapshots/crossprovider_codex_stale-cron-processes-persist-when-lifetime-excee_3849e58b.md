---
name: crossprovider codex stale-cron-processes-persist-when-lifetime-excee
description: Stale cron processes persist when lifetime exceeds schedule interval
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cron, audit, process-lifecycle]
---

A 4-hour cron job that started 8h42m ago has survived two full subsequent schedule cycles. This indicates stall, retry, or incorrect timeout rather than just age. Process + schedule audit together: compare PID start time against crontab interval and check whether multiple instances of the same job are concurrently running.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
