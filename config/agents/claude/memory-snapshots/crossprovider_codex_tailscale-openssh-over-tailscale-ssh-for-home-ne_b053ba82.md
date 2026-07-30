---
name: crossprovider codex tailscale-openssh-over-tailscale-ssh-for-home-ne
description: Tailscale + OpenSSH over Tailscale SSH for home network remote access
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [ssh, networking, security]
---

For remote SSH through home NAT/CGNAT with changing ISPs, pair Tailscale VPN (survives IP changes, uses DERP relays as fallback) with conventional OpenSSH key authentication, not Tailscale's built-in SSH. This gives two independent security controls and is more predictable for unattended automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
