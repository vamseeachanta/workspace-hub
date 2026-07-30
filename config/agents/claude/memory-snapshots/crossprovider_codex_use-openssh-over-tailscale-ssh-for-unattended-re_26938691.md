---
name: crossprovider codex use-openssh-over-tailscale-ssh-for-unattended-re
description: Use OpenSSH over Tailscale SSH for unattended remote systems
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [networking, remote-access, automation, security, tailscale]
---

Tailscale SSH delegates authentication to the identity provider and tailnet policy, creating a single point of failure for account access. Conventional OpenSSH with keys running over Tailscale's network layer provides two independent controls: device membership in the tailnet + SSH key possession. This is simpler, more predictable for automation, and better for multi-user and account-recovery scenarios. Use password-protected keys held in an agent, TPM, or hardware security key rather than loose private key files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
