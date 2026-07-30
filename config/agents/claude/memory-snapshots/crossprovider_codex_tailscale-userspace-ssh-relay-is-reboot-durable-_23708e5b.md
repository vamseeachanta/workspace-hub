---
name: crossprovider codex tailscale-userspace-ssh-relay-is-reboot-durable-
description: Tailscale userspace SSH relay is reboot-durable and suitable for remote travel
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [tailscale, ssh, remote-access, travel-readiness]
---

SSH via Tailscale relay persists across reboot without GUI login, has valid node keys (tested to Jan 2027), and achieves ~50 ms latency over cellular. Suitable for remote access during travel; pair with key-based auth (not password-only) and pre-travel end-to-end test.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
