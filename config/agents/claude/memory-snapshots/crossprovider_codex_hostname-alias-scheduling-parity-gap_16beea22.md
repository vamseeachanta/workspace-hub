---
name: crossprovider codex hostname-alias-scheduling-parity-gap
description: Hostname-alias scheduling parity gap
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-scheduler, hostname-aliases, validation-gap, parity-check]
---

`setup-cron.sh` installs tasks when raw hostname appears in `machines` list, but validation accepts registry alias tokens. This creates divergence: validation passes but installation/monitoring may fail or differ on alias hosts. Future scheduled-task features must verify alias-token parity between installer and health-check.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
