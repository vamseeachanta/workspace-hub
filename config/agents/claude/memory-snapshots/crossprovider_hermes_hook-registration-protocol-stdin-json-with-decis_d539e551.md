---
name: crossprovider hermes hook-registration-protocol-stdin-json-with-decis
description: Hook registration protocol: stdin JSON with decision block
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hooks, protocol, enforcement]
---

PreToolUse hooks (e.g., cross-review-gate.sh) receive JSON stdin: `{tool_name, tool_input: {command, ...}}`. To block: output `{decision: 'block', reason: '...'}` to stdout and exit 0. To allow: exit 0 with no output. Non-zero exit is NOT used for blocking (hook always exits 0). Protocol is the same for all tool-matching PreToolUse hooks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
