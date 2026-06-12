---
name: crossprovider gemini cron-shell-redirection-evaluates-before-script-s
description: Cron shell redirection evaluates before script startup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cron, shell-timing, workspace-hub]
---

The `>>` redirection in cron commands (e.g., `command >> $WORKSPACE_HUB/logs/file.log`) is evaluated by the shell BEFORE the referenced script executes. If `$WORKSPACE_HUB` or target directory is unset/missing, the job fails silently at invocation, not at runtime. Pre-create log directories in setup or use wrapper scripts to establish env before redirection.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
