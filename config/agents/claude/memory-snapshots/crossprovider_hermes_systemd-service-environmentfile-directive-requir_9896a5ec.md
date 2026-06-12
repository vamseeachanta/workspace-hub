---
name: crossprovider hermes systemd-service-environmentfile-directive-requir
description: Systemd service EnvironmentFile directive required for Hermes gateway
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, systemd, gateway, configuration]
---

Hermes gateway service needs explicit `EnvironmentFile=/home/vamsee/.hermes/.env` in a systemd drop-in file plus `TimeoutStopSec=210` for proper startup/shutdown. Just having the `.env` file present isn't sufficient; systemd must be configured to load it. Non-interactive sudo blocks installation of systemd changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
