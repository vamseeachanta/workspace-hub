---
name: crossprovider hermes claude-print-mode-requires-either-stdin-or-promp
description: claude --print mode requires either stdin or prompt argument
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-cli, error-handling, flags]
---

Running `claude --print` without piped input or `-p` prompt argument fails with "Input must be provided either through stdin or as a prompt argument". For unattended backgrounded runs, always provide the prompt via `-p` flag or stdin.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
