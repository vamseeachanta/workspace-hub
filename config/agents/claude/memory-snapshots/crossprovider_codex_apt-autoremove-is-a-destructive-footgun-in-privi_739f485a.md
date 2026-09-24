---
name: crossprovider codex apt-autoremove-is-a-destructive-footgun-in-privi
description: apt autoremove is a destructive footgun in privileged cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [package-management, privilege-escalation, system-safety]
---

Sandbox simulation of apt autoremove proposed removing 266 packages including development libraries and NVIDIA firmware. Safe pattern: use only native cache-specific commands (apt autoclean, npm cache clean), keep package removal report-only, and enforce privilege boundaries (user-space caches only, system journal rotation stays blocked without sudo).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
