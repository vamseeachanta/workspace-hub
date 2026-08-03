---
name: crossprovider codex cron-overlap-requires-process-group-tracking-not
description: Cron overlap requires process-group tracking, not log freshness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cron, operations, monitoring]
---

Scheduled job overlap and hangs are not detected by log-update timestamps alone; must track process groups by task ID, classify filesystem-wait conditions (e.g., FUSE mount timeouts), and enforce singleton locks for mutating jobs. Long-running stalled processes appear recent-but-healthy if a child touches the log.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
