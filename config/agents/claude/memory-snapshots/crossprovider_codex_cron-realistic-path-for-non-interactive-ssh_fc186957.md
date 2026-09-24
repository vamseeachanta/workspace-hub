---
name: crossprovider codex cron-realistic-path-for-non-interactive-ssh
description: Cron-realistic PATH for non-interactive SSH
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ssh, cron, environment, multi-host]
---

Non-interactive SSH shells don't source ~/.bashrc, so explicit PATH prefix is required for tools like npm and git. For multi-host audit scripts running from cron, prepend `PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH` to SSH commands to match expected tool locations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
