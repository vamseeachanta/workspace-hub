---
name: crossprovider gemini gemini-cli-requires-y-flag-for-non-interactive-m
description: Gemini CLI requires -y flag for non-interactive mode and stdin piping
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [gemini-cli, tooling-quirk, non-interactive]
---

Plans using Gemini CLI must include `-y` flag to prevent hanging on input prompts and must pipe content via stdin (`cat file | gemini -p prompt -y`), not pass file paths as arguments. File-path arguments are silently ignored.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
