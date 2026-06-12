---
name: crossprovider hermes windows-registry-hosts-with-ssh-null-break-cross
description: Windows registry hosts with ssh:null break cross-platform reachability probes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-os-dispatch, registry-schema, ssh-assumption]
---

Standard reachability probes assume SSH is available for non-Linux hosts. Registry entries with `ssh: null` and `tailscale_ip: null` (e.g., licensed-win-1, licensed-win-2) fail DNS/SSH probes; need separate evidence-collection paths for physical-only or non-SSH hosts. Readiness code only covers Linux evidence paths explicitly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
