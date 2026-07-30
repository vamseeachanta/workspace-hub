---
name: crossprovider codex pre-travel-ssh-hardening-end-to-end-verification
description: Pre-travel SSH hardening: end-to-end verification checklist
metadata:
  type: reference
  source: codex
  bridged: 2026-07-22
  tags: [ssh, tailscale, remote-access, pre-trip]
---

Before remote access during travel, verify: SSH daemon active on :22, Tailscale userspace relay running with zero warnings, both auto-restart without GUI, firewall rules absent, AC power-loss recovery enabled, and run end-to-end test over cellular: `ssh vamsee@100.105.46.79 'hostname && uptime'`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
