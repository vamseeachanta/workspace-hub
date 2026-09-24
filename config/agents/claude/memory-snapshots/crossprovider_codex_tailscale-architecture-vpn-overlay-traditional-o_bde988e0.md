---
name: crossprovider codex tailscale-architecture-vpn-overlay-traditional-o
description: Tailscale architecture: VPN overlay + traditional OpenSSH, not Tailscale SSH
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, security, ssh]
---

Use Tailscale for the private network layer (survives IP changes, NAT, CGNAT, hotel networks) and conventional OpenSSH with keys for authentication. Tailscale SSH makes identity provider the auth authority; traditional keys give independent control and resilience to account/control-plane issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
