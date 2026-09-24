---
name: crossprovider codex bash-function-return-pattern-using-printf-v-for-
description: Bash function return pattern using printf -v for set -e safety
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, error-handling, shell-scripting]
---

In set -e contexts, return values from functions via printf -v varname instead of echo to caller's variable. Pair with module-level error variables (e.g., resolve_install_root_error) to propagate error messages without stdout capture ambiguity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
