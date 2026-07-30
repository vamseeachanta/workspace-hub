---
name: crossprovider codex dual-layer-authentication-is-more-resilient-than
description: Dual-layer authentication is more resilient than single-plane control
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [infrastructure, security, authentication]
---

Network-layer access control (e.g., Tailscale VPN) + SSH key authentication provide independent failure domains and recover better from ISP IP changes/CGNAT. Prefer conventional OpenSSH keys over identity-provider-dependent SSH for unattended automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
