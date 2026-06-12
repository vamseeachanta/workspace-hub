---
name: crossprovider codex shell-context-piping-hits-arg-length-limits-with
description: Shell context piping hits arg-length limits with large WRK items
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-orchestration, performance, argv-limits]
---

Passing large markdown context as a single CLI argument (`claude -p "$(cat file)"`) hits OS argv limits (~128KB). Use stdin piping (`echo $CONTEXT | claude -p`) or write context to temp files and read via stdin instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
