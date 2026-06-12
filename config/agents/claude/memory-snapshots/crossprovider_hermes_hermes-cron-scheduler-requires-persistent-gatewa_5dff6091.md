---
name: crossprovider hermes hermes-cron-scheduler-requires-persistent-gatewa
description: Hermes cron scheduler requires persistent Gateway process
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, cron, process-management]
---

Hermes internal cron jobs (gmail-digest, memory-bridge) fail if Gateway process dies. Manual `hermes gateway --detach` doesn't persist across reboots. Use systemd service or monitor with `pgrep hermes-gateway` in startup scripts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
