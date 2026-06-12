---
name: crossprovider gemini arbitrary-code-execution-from-editable-files-is-
description: Arbitrary code execution from editable files is critical security risk
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [security, acl-vulnerability, command-execution]
---

Executing commands extracted from user-editable files (memory bullets, config files, etc.) is an ACE vulnerability even as opt-in feature. WRK-637 memory compaction rejected `--check-commands` rule due to this. Safer approach: validate command presence via static checks (grep, which) without execution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
