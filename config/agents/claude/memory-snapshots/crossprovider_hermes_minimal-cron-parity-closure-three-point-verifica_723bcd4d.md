---
name: crossprovider hermes minimal-cron-parity-closure-three-point-verifica
description: Minimal cron parity closure: three-point verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-ops, closure-verification, settled-truths]
---

Credible cron closure requires: (1) validate-schedule.py YAML syntax, (2) setup-cron.sh --dry-run canonical entries, (3) crontab -l live entries diff. Cron-health logs are secondary monitors; they cannot prove parity alone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
