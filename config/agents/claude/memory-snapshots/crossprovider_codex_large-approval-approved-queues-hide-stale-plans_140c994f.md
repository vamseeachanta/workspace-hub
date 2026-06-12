---
name: crossprovider codex large-approval-approved-queues-hide-stale-plans
description: Large approval-approved queues hide stale plans
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-lifecycle, queue-hygiene, stale-detection]
---

When the `plan-approved` queue exceeds 15–20 items, periodic reconciliation is needed: does the plan file still exist? Does it match the issue body date? Plans older than one week should be flagged for sync, archive, or reassess. Label age ≠ plan freshness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
