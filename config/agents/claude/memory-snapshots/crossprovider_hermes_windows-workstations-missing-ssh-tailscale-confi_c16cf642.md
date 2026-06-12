---
name: crossprovider hermes windows-workstations-missing-ssh-tailscale-confi
description: Windows workstations missing SSH/Tailscale config blocks multi-machine dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram-dispatch, multi-machine, windows, blocker]
---

licensed-win-1 and licensed-win-2 in workstations/registry.yaml have ssh: null and tailscale_ip: null. Multi-machine Telegram dispatch cannot reach these hosts without SSH and Tailscale configuration. Reachability probe showed DNS failures for Windows hosts; this is the root cause blocking cross-machine dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
