---
name: crossprovider hermes cron-environment-lacks-home-use-absolute-paths
description: Cron environment lacks $HOME; use absolute paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, environment, bash]
---

Cron context doesn't reliably set $HOME. Scripts using `$HOME/.local/bin/uv` fail with 'command not found'. Use absolute path `/home/username/.local/bin/uv` instead. Affects any PATH-dependent tool.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
