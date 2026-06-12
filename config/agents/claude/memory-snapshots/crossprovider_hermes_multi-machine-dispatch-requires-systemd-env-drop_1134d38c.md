---
name: crossprovider hermes multi-machine-dispatch-requires-systemd-env-drop
description: Multi-machine dispatch requires systemd env-drops, local readiness proof per host, and hardened timeouts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, systemd, multi-machine, readiness]
---

Interactive shell env-vars are not loaded by systemd; must use systemd drop-in EnvironmentFile. Each remote worker needs host-local readiness evidence (not coordinator-side SSH inference). Default 60s TimeoutStopSec insufficient; harden to 210s+ for gateway drain. Dirty workspaces are blocking dependencies.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
