---
name: crossprovider codex tailscale-traditional-openssh-over-tailscale-ssh
description: Tailscale + traditional OpenSSH over Tailscale SSH
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, infrastructure, security]
---

Use Tailscale as the VPN overlay network layer with conventional OpenSSH keys for authentication. This provides two independent security controls (tailnet membership + key possession) and better compatibility with unattended automation, deployment scripting, and credential agents than Tailscale SSH's identity-provider-driven auth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
