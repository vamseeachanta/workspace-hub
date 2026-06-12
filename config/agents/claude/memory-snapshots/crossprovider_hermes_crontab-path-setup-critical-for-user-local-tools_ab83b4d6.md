---
name: crossprovider hermes crontab-path-setup-critical-for-user-local-tools
description: Crontab PATH setup critical for user-local tools
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-debugging, environment-setup, automation-reliability]
---

Crontab entries fail silently when commands installed in user-local directories (e.g., ~/.local/bin) aren't found—must explicitly set `PATH=$HOME/.local/bin:$PATH` in the crontab line. Common failure: `uv: command not found` despite `uv` working in interactive shells.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
