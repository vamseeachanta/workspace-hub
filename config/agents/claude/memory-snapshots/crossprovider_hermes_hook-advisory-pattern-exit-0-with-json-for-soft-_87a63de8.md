---
name: crossprovider hermes hook-advisory-pattern-exit-0-with-json-for-soft-
description: Hook advisory pattern: exit 0 with JSON for soft gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hooks, compliance, claude-code-harness]
---

Claude Code PreToolUse hooks signal block/advice by exiting 0 with JSON (`{"decision":"block","reason":"..."}`) instead of failing hard. Allows compliance gates to signal without killing tool execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
