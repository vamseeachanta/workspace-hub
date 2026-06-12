---
name: crossprovider hermes systemd-environmentfile-requires-explicit-unit-f
description: systemd EnvironmentFile requires explicit unit-file wiring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [operations, systemd, multi-machine, secrets]
---

For multi-machine agent coordination (Telegram/Hermes), secrets in ~/.hermes/.env load only if systemd unit file explicitly lists EnvironmentFile=/path/to/.env; file existence alone insufficient. Also require TimeoutStopSec >= 210s for graceful agent shutdown during cleanup.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
