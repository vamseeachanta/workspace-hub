---
name: crossprovider codex tailscale-overlay-with-conventional-openssh-for-
description: Tailscale overlay with conventional OpenSSH for production automation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [ssh, tailscale, remote-access, automation, architecture]
---

Use Tailscale as a private network layer paired with conventional OpenSSH keys—not Tailscale SSH itself—for unattended automation and recovery. Tailscale SSH is convenient for interactive use but depends on account/control-plane state and has automation caveats; OpenSSH over Tailscale is simpler and more failure-resistant. Enable device approval and MFA on the identity account, and use device tags for least-privilege access control.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
