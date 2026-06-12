---
name: crossprovider hermes hermes-cron-jobs-require-gateway-process-running
description: Hermes cron jobs require gateway process running as systemd service
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, cron, infrastructure, tooling-quirk]
---

Hermes cron ticker runs inside the gateway process; when gateway stops, all scheduled jobs fail silently with no error. Start via systemd (`hermes-gateway.service` or manual systemd unit), not `--detach` flag.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
