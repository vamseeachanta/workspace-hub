---
name: crossprovider gemini gemini-cli-non-interactive-syntax-requires-y-fla
description: Gemini CLI non-interactive syntax requires -y flag and stdin piping
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gemini, cli-syntax, non-interactive]
---

Gemini background execution needs `cat file | gemini -p "prompt" -y` (stdin piping + `-y` flag). Direct file arguments or missing `-y` will cause the process to hang waiting for user interaction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
