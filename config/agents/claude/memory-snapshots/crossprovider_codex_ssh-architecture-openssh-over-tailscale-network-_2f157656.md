---
name: crossprovider codex ssh-architecture-openssh-over-tailscale-network-
description: SSH architecture: OpenSSH over Tailscale network rather than Tailscale SSH
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ssh, security-architecture, tailscale, remote-access]
---

For systems requiring remote access via Tailscale, use conventional OpenSSH with keys over Tailscale's network layer, rather than `tailscale ssh`. This architecture provides two independent security controls (tailnet membership + SSH key possession), avoids identity-provider account dependency, and simplifies unattended automation. Tailscale SSH is more convenient but makes the identity authentication the sole control point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
