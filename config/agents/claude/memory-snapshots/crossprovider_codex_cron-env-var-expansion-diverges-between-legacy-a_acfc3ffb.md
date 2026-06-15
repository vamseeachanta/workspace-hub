---
name: crossprovider codex cron-env-var-expansion-diverges-between-legacy-a
description: Cron env-var expansion diverges between legacy and transactional paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, environment-variables, transactional-cron]
---

setup-cron.sh expands $WORKSPACE_HUB and $LOG variables, but cron_apply.py → cron_transaction.render_block() does not. Catalog tasks with placeholders work under the legacy installer but fail under the transactional installer, creating a hidden upgrade hazard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
