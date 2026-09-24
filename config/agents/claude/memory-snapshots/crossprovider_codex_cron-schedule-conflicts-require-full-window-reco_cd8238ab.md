---
name: crossprovider codex cron-schedule-conflicts-require-full-window-reco
description: Cron schedule conflicts require full-window reconciliation, not partial slot shifts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, scheduling, conflict-resolution]
---

Shifting a job from 03:00 to 03:15 does not eliminate conflict if the job runs 60s and other jobs start at 03:30. Must either fully resolve the time window or explicitly document/accept overlap. Partial mitigation without conflict resolution is still REQUEST_CHANGES.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
