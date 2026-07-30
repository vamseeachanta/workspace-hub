---
name: crossprovider codex layered-security-vpn-ssh-keys-over-convenience-f
description: Layered security: VPN + SSH keys over convenience features
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [security, remote-access, architecture]
---

For remote machine access, combine a VPN layer (e.g., Tailscale) with traditional SSH key authentication instead of relying on single identity-provider auth (e.g., Tailscale SSH). Two independent controls survive partial failures better and avoid vendor lock-in on identity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
