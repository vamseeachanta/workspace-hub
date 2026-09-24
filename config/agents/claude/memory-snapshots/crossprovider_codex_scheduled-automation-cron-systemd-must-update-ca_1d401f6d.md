---
name: crossprovider codex scheduled-automation-cron-systemd-must-update-ca
description: Scheduled automation (cron/systemd) must update canonical install scripts, not templates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-management, scheduling, reproducibility]
---

For recurring jobs, update the authoritative installation source (e.g., setup-cron.sh ENTRIES array) not the reference template. Templates are documentation; the install script is execution. A later `setup-cron.sh` run will overwrite template-only edits, losing the job.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
