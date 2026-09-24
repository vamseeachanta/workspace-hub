---
name: crossprovider codex scheduled-task-config-drift-silently-breaks-publ
description: Scheduled task config drift silently breaks publication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduling, automation, config-drift]
---

Canonical schedule YAML specifies `bridge-hermes-claude.sh --commit` but installed crontab omits it, placing tasks in dry-run mode without alerts. Logs report success while publication silently stops. Verify scheduler convergence against source before trusting heartbeat/freshness claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
