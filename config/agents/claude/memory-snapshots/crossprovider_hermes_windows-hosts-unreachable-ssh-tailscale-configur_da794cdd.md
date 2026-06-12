---
name: crossprovider hermes windows-hosts-unreachable-ssh-tailscale-configur
description: Windows hosts unreachable: ssh/tailscale configured null in registry
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-os, dispatch, registry, windows-constraint]
---

Windows machines (licensed-win-1, licensed-win-2) in config/workstations/registry.yaml have `ssh: null` and `tailscale_ip: null`, causing DNS resolution failure ("Temporary failure in name resolution") and SSH probe failures. Dispatch routing must handle Windows as physical-only or require alternative transport layer.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
