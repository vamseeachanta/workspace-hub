---
name: crossprovider codex tailscale-openssh-provides-two-independent-ssh-a
description: Tailscale + OpenSSH provides two independent SSH authentication controls
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [remote-access, architecture, authentication]
---

Conventional OpenSSH with keys over Tailscale's private network provides independent authentication gates: tailnet membership (device layer) plus SSH key (user layer). More predictable for automation and multi-user scenarios than Tailscale SSH alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
