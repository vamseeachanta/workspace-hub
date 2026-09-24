---
name: crossprovider codex path-visibility-and-package-presence-are-separat
description: PATH visibility and package presence are separate problems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-environment, troubleshooting, systemd]
---

A package may be installed but unreachable in the contexts where it's needed: non-login shells, systemd units, cron jobs. Testing for availability must use the actual execution context, not just 'which' against the interactive shell. Profile-only PATH additions (e.g., `~/.local/bin`) are invisible to non-login contexts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
