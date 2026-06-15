---
name: crossprovider codex string-based-variable-expansion-breaks-on-prefix
description: String-based variable expansion breaks on prefix boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [templating, variable-expansion, config-centralization]
---

Raw string replacement (`.replace("$WORKSPACE_HUB", ...)`) corrupts variables with those prefixes: `$WORKSPACE_HUB_BACKUP` becomes `/repo_BACKUP`, `$LOGDIR` becomes `/tmp/workspace-hub-cron.logDIR`. Solution: use exact variable names or braced forms (`${VAR}`) only, never prefix-based replacement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
