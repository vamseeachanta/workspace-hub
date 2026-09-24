---
name: crossprovider codex cron-installation-requires-edits-to-both-templat
description: Cron installation requires edits to both template and installer script
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, installation, deployment]
---

Updating `crontab-template.sh` alone does not install cron jobs. The live installer (setup-cron.sh) builds its own ENTRIES array and must be edited alongside the template. Verify the installer wiring before assuming template changes propagate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
