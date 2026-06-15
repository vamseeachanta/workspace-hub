---
name: crossprovider codex machine-specific-cron-filtering-requires-per-hos
description: Machine-specific cron filtering requires per-host evidence gathering
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, testing, infrastructure]
---

setup-cron.sh filters scheduled tasks by hostname -s, so dry-run evidence for schedule validity must be gathered on each target machine. Host-independent coverage (syntax, logic) belongs in validate-schedule.py; cross-machine testing happens on live hosts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
