---
name: crossprovider codex sourced-bash-libraries-must-validate-inputs-expl
description: Sourced bash libraries must validate inputs explicitly, not execute variable values
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash-safety, sourced-libraries, command-injection]
---

When a bash file is sourced (e.g., `source download-helpers.sh`), avoid patterns like `if "${VARIABLE}"; then` which execute the variable as a shell command. Use explicit comparison: `[[ "${DRY_RUN}" == "true" ]]`. Also ensure sourced functions return meaningful exit codes on failure, not just the status of cleanup commands (e.g., `rm -f` always returns 0).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
