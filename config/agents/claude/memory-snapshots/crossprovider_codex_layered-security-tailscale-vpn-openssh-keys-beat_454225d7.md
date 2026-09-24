---
name: crossprovider codex layered-security-tailscale-vpn-openssh-keys-beat
description: Layered security: Tailscale VPN + OpenSSH keys beats Tailscale SSH alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, ssh, architecture]
---

For unattended automation and recovery, use Tailscale as the private network layer with conventional OpenSSH and key-based auth on top. This gives two independent controls (membership + possession) and is simpler than Tailscale SSH during control-plane outages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
