---
name: crossprovider gemini bash-shared-utilities-must-use-safe-boolean-comp
description: Bash shared utilities must use safe boolean comparison and mkdir
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, shell-safety, shared-utilities]
---

Never `if "${DRY_RUN}"` (executes variable as command). Use `[[ "${DRY_RUN}" == "true" ]]`. Always `mkdir -p` before writes. Prevents command-injection and missing-directory errors in shared shell functions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
