---
name: crossprovider gemini cron-shell-redirection-timing-failure-mode
description: Cron shell redirection timing failure mode
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cron, shell, environment-variables, timing, bootstrap-failure]
---

Outer-level redirections in cron commands (`>> /path/file.log 2>&1`) are evaluated by the shell BEFORE the wrapper script executes. If the target directory doesn't exist or required environment variables (e.g., `$WORKSPACE_HUB`) are unset, the redirection fails at shell parse time, and the script never starts—distinct from script runtime failure. This creates a silent-before-bootstrap failure signature that cron health monitors cannot distinguish from missing cron entries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
