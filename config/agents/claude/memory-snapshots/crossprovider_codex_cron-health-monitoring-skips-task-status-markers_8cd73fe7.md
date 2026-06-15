---
name: crossprovider codex cron-health-monitoring-skips-task-status-markers
description: Cron-health monitoring skips task=status markers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, monitoring, pattern-matching]
---

cron-health-check.sh detects execution failures by scanning generic ERROR:, fatal:, and trace patterns. Tasks that emit structured status lines like 'task=repo-ecosystem-hygiene status=ERROR' are invisible to health monitoring. New cron tasks must include ERROR: prefix in error output or cron-health will miss failures entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
