---
name: crossprovider codex architecture-ssh-over-vpn-overlay-with-independe
description: Architecture: SSH over VPN overlay with independent auth
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, ssh, networking, security]
---

For remote SSH over unreliable networks (ISP IP changes, CGNAT, mobile): use Tailscale (or WireGuard) as the VPN overlay for connectivity, with conventional OpenSSH and key-based auth as the separate SSH layer. This provides two independent security boundaries and is more predictable for unattended automation than integrated SSH-over-VPN solutions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
