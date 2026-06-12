---
name: crossprovider hermes windows-workstations-lack-ssh-tailscale-registry
description: Windows workstations lack SSH/Tailscale registry entries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, windows, registry, network]
---

licensed-win-1 and licensed-win-2 in config/workstations/registry.yaml have ssh: null and tailscale_ip: null, blocking multi-machine dispatch from control plane. Reachability probes fail with DNS resolution errors for Windows hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
