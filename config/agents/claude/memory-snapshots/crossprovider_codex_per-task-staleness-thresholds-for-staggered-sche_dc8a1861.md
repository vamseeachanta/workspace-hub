---
name: crossprovider codex per-task-staleness-thresholds-for-staggered-sche
description: Per-task staleness thresholds for staggered schedules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, staleness-detection, scheduling, thresholds]
---

Fixed freshness windows (e.g., 25-hour threshold) are too rigid when scheduled tasks run at different times/frequencies. A 05:35 daily task checked at 05:45 can miss one run and still be within 24h10m; per-task stale thresholds are required. Monitoring systems with variable task cadences need configurable thresholds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
