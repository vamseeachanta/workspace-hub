---
name: crossprovider codex cron-health-classification-misses-structured-sta
description: Cron-health classification misses structured status lines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, log-parsing, status-detection, structured-logs]
---

`cron-health-check.sh` pattern-matches generic error tokens like `ERROR:` and `fatal:`, missing explicit structured status like `task=<id> status=ERROR`. Health monitoring requires both generic error detection AND task-specific structured-log parsing for accurate classification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
