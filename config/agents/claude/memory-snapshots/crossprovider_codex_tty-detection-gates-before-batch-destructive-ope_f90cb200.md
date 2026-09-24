---
name: crossprovider codex tty-detection-gates-before-batch-destructive-ope
description: TTY detection gates before batch destructive operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli, safety, ux, git]
---

Use `[ -t 1 ]` to detect interactive terminal. Gate parallel commits/syncs with a countdown prompt only when interactive, allowing scripted batch runs to proceed without confirmation. Improves UX for operations that mutate multiple repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
