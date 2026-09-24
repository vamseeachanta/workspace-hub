---
name: crossprovider codex bash-process-substitution-with-error-redirect-si
description: Bash process substitution with error redirect silences exit codes under set -e
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, error-handling, shell-gotcha]
---

When capturing process substitution output via `<(command) 2>&1` in a read loop, the loop won't detect producer failures even with `set -e` active—the shell treats the redirect success, not the producer's exit code. Must explicitly capture to temp file and check exit status, or use command substitution `$(...)` instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
