---
name: crossprovider codex tailscale-conventional-openssh-for-remote-access
description: Tailscale + conventional OpenSSH for remote access robustness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ssh, tailscale, remote-access, architecture]
---

Use Tailscale as private network transport with conventional OpenSSH keys, not Tailscale SSH. This provides two independent auth controls (tailnet membership + SSH key) and better supports unattended automation. Tailscale SSH ties auth to identity-provider account state, which is fragile for headless pipelines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
