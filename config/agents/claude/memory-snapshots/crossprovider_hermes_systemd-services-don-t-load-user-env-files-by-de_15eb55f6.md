---
name: crossprovider hermes systemd-services-don-t-load-user-env-files-by-de
description: Systemd services don't load user env files by default
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [systemd, daemon-config, env-vars]
---

Systemd-spawned services ignore `~/.bashrc` and `~/.env`. Must add `EnvironmentFile=/path/to/.env` to the service unit file for env vars to load at boot. Applies to all daemons: Hermes gateway, monitoring, cron runners.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
