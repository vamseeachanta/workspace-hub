---
name: crossprovider gemini generated-shell-hooks-can-have-dead-code-after-e
description: Generated shell hooks can have dead code after exit/return statements
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hooks, code-generation, shell, verification]
---

When composing shell hooks via concatenation or template substitution, verify all blocks are reachable; code appended after `exit` or `return` statements will never execute. This is a code-generation hazard specific to hook installation scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
