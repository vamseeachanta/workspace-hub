---
name: crossprovider codex cron-task-log-indirection-creates-audit-freshnes
description: Cron task log indirection creates audit-freshness hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, monitoring, shell-scripting, log-routing]
---

Scheduled tasks declare `log:` paths in config (e.g., `logs/repository-sync-*.log`) but actual output may redirect via environment variables like `$LOG`, landing elsewhere (e.g., `logs/quality/cron-wrapper.log`). Log freshness inference is unreliable across different cron wrapper implementations; verifying task health requires reading the cron runner's actual output, not the declared config path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
