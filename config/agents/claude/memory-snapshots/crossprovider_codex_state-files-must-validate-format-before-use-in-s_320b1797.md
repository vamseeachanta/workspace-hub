---
name: crossprovider codex state-files-must-validate-format-before-use-in-s
description: State files must validate format before use in shell
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-scripting, input-validation, security]
---

Reading state files in shell scripts should include format validation (regex checks) before echoing or using in subshells; tampered or corrupted state can inject terminal control characters or command sequences. Even for shell, treat external state as untrusted input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
