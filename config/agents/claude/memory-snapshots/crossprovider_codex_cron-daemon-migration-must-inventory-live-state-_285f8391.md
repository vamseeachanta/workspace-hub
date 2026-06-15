---
name: crossprovider codex cron-daemon-migration-must-inventory-live-state-
description: Cron/daemon migration must inventory live state, preserve explicitly, and verify post-cutover
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [infrastructure-planning, cron-safety, operational-preservation]
---

Infrastructure cutover ('shadow cron then cutover') fails silently if 'clean' is undefined. Require: (1) inventory current live cron jobs (crontab -l), commit as evidence; (2) define preserve/remove/classify rules with generated-block ownership markers; (3) provide backup and restore commands; (4) add post-migration live daemon verification to acceptance criteria. Prevents undetected loss of operationally-required jobs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
