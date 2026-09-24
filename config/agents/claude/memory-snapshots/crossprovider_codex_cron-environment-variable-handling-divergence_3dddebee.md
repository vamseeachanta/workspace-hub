---
name: crossprovider codex cron-environment-variable-handling-divergence
description: Cron environment variable handling divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, env-vars, architectural-split]
---

`setup-cron.sh` expands `$WORKSPACE_HUB` and `$LOG` before writing crontab, but `cron_apply.py` → `cron_transaction.render_block()` has no expansion logic, causing placeholders to survive into the managed block. Live crontabs rendered via `cron_apply` are unexecutable without manual env-var insertion. Future cron work must unify these paths or explicitly document incompatibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
