---
name: crossprovider codex tailscale-vpn-conventional-openssh-for-automatio
description: Tailscale VPN + conventional OpenSSH for automation-friendly remote access
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [networking, security, automation, remote-access]
---

Use Tailscale as the VPN/relay layer (handles NAT, ISP-IP changes, fallback relays) combined with traditional OpenSSH key authentication. This provides dual controls (network membership + key possession) and avoids provider-account dependency for unattended automation. Harden sshd with PasswordAuthentication no, PubkeyAuthentication yes, and AllowUsers scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
