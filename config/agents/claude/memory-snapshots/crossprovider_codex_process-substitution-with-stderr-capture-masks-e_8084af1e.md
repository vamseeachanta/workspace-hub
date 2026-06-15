---
name: crossprovider codex process-substitution-with-stderr-capture-masks-e
description: Process substitution with stderr capture masks exit codes in Bash loops
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell-behavior, cron-setup, process-substitution, error-handling]
---

Bash loop + process substitution with `2>&1` redirection ignores the producer's exit code, treating partial/malformed output as valid entries. In setup-cron.sh, renderer failures were silently captured as cron entries instead of blocking. Fix: render to temp file, check exit code explicitly, keep stderr out of the output stream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
