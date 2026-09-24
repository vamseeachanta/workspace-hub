---
name: crossprovider codex tailscale-overlay-openssh-for-unattended-remote-
description: Tailscale overlay + OpenSSH for unattended remote access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, networking, ssh]
---

Use Tailscale VPN + conventional OpenSSH key authentication (not Tailscale SSH) for unattended multi-machine automation through ISP IP changes and CGNAT. Two independent auth layers (tailnet membership + SSH key) are more predictable than account-based SSH.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
