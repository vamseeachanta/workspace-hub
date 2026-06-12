---
name: crossprovider hermes systemd-daemon-config-environmentfile-timeoutsto
description: Systemd daemon config: EnvironmentFile + TimeoutStopSec pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [systemd, hermes, daemon-config]
---

For systemd services that need environment variables and extended shutdown time (e.g., Hermes gateway), use a drop-in override at `/etc/systemd/system/<service>.d/10-<name>.conf` with `[Service]` section containing `EnvironmentFile=<path>` and `TimeoutStopSec=<seconds>`; then `daemon-reload` and `restart`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
