---
name: crossprovider codex claude-cli-tools-argument-ordering-consumes-trai
description: Claude CLI --tools argument ordering consumes trailing prompt
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [claude-cli, argument-ordering, tooling-quirk]
---

Claude's variadic `--tools` option consumes all remaining arguments. Correct form: `claude ... --tools <names> --prompt <prompt>`. Reversed order causes parse failure with 'Input must be provided' before model execution even starts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
