---
name: crossprovider codex cron-dry-run-metadata-doesn-t-validate-full-exec
description: Cron dry-run metadata doesn't validate full executability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, dry-run, testing, validation]
---

cron_apply.py --json returns only task selection/preservation metadata, not the rendered final crontab or env contract. Dry-run cannot prove a plan is executable without actually rendering and validating the environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
