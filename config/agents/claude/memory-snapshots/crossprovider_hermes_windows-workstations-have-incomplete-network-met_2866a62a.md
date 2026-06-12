---
name: crossprovider hermes windows-workstations-have-incomplete-network-met
description: Windows workstations have incomplete network metadata in registry
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows-hosts, network-metadata, multi-machine, workspace-hub-2524]
---

Workspace-hub config/workstations/registry.yaml entries for licensed-win-1 and licensed-win-2 have `ssh: null` and `tailscale_ip: null`, making SSH-based reachability probes fail. Multi-machine orchestration needs alternative reachability paths (WinRM, serial, etc.) for Windows hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
