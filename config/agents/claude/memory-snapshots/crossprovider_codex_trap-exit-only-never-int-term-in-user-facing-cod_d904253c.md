---
name: crossprovider codex trap-exit-only-never-int-term-in-user-facing-cod
description: Trap EXIT only, never INT/TERM in user-facing code
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, signal-handling, ux]
---

Trapping INT/TERM overrides bash's default abort behavior: the handler runs but execution continues. On Ctrl+C, bash exits and EXIT trap fires cleanly. For foreground scripts, omit INT/TERM to preserve interrupt semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
