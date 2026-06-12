---
name: crossprovider hermes claude-cli-launcher-arg-wrapping-causes-flag-par
description: Claude CLI launcher arg-wrapping causes flag parsing errors
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell, claude-cli, launcher-pattern]
---

Long single-line `claude -p` commands with `--max-budget-usd` fail when wrapped mid-flag (e.g., line break after `--max`), causing bash to interpret `-budget-usd` as a new command yielding `-budget-usd: command not found`. Safe pattern: use argv arrays, absolute `$CLAUDE_BIN` path, fully quoted variables, explicit smoke checks on binary and flag support before execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
