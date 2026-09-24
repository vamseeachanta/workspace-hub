---
name: crossprovider codex cron-audit-windows-with-timezone-naive-date-calc
description: Cron audit windows with timezone-naive date calculation miscount boundary commits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, time, git]
---

Audits computing a 24-hour window in local wall-clock time but comparing against git commit timestamps (which embed author timezone offsets) can double-count or skip commits around midnight. Use UTC-normalized time throughout; convert git timestamps to UTC before windowing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
