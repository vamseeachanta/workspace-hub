---
name: crossprovider codex tailscale-openssh-for-unattended-remote-ssh-thro
description: Tailscale + OpenSSH for unattended remote SSH through changing networks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [infrastructure, ssh, architecture, automation]
---

Use Tailscale as the network layer with conventional OpenSSH key authentication (not Tailscale SSH) for unattended automation. Provides two independent security controls: device membership + SSH key. Survives ISP IP changes and hotel/mobile networks via DERP relays.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
