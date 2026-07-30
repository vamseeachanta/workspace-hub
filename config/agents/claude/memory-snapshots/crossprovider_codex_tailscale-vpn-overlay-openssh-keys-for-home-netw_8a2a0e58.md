---
name: crossprovider codex tailscale-vpn-overlay-openssh-keys-for-home-netw
description: Tailscale VPN overlay + OpenSSH keys for home-networked remote Linux
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [architecture, security, ssh, automation, networking]
---

Use Tailscale as the VPN overlay layer only, with conventional OpenSSH public-key authentication (not Tailscale SSH). This provides two independent security boundaries: tailnet membership plus key possession. Tailscale SSH is convenient interactively but unsuitable for automation—it makes the identity provider account the single SSH authority, incompatible with deterministic key-based unattended access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
