---
name: crossprovider codex cron-slot-conflicts-require-explicit-margin-calc
description: Cron slot conflicts require explicit margin calculation and policy
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, operations, scheduling]
---

When adding a new periodic job to cron, confirm no overlap with existing jobs accounting for actual runtime + timeout. Sunday 03:15 + 60s timeout = completes 03:16, non-overlapping with 03:30 job = 14-min buffer. But if multiple Sunday maintenance windows exist, confirm all + document acceptance of any residual overlap or require scheduling in non-maintenance windows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
