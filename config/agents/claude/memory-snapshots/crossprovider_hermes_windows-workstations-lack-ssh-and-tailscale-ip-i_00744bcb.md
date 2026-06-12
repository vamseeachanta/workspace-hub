---
name: crossprovider hermes windows-workstations-lack-ssh-and-tailscale-ip-i
description: Windows workstations lack SSH and Tailscale IP in multi-machine setup
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, orchestration-blocker, windows-gaps, env-fact]
---

licensed-win-1 and licensed-win-2 have ssh=null and tailscale_ip=null in registry.yaml; DNS fails. Blocks unified Hermes dispatch across machines. Requires SSH proxy or Tailscale enablement for Windows orchestration.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
