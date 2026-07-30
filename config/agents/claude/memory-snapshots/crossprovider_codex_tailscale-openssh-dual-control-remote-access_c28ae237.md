---
name: crossprovider codex tailscale-openssh-dual-control-remote-access
description: Tailscale + OpenSSH dual-control remote access
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [remote-access, ssh, network-architecture]
---

Use Tailscale as the private network layer and conventional OpenSSH with key authentication as the independent auth authority. This provides two orthogonal controls: device must belong to tailnet AND must present authorized key. Survives ISP IP changes, CGNAT, and hotel/mobile networks via DERP fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
