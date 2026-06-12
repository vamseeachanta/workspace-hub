---
name: crossprovider hermes stdin-redirection-is-more-reliable-than-file-rea
description: stdin redirection is more reliable than file-read prompts for unattended Claude runs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-cli, unattended-execution, prompt-delivery]
---

Pattern `claude -p "prompt" < file.md` is more robust than `claude -p "Read file X and execute"`; the latter can fail silently in background execution. stdin redirection ensures the full prompt body is delivered directly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
