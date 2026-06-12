---
name: crossprovider hermes hermes-systemd-integration-requires-explicit-env
description: Hermes systemd integration requires explicit EnvironmentFile drop-in
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, systemd, multi-machine-dispatch]
---

Hermes gateway does not auto-load `~/.hermes/.env` on startup. Must create systemd drop-in with `EnvironmentFile=/home/vamsee/.hermes/.env` and `TimeoutStopSec=210` (or higher) for safe shutdown of dispatch operations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
