---
name: crossprovider codex json-envelope-must-wrap-argument-parsing-not-fol
description: JSON envelope must wrap argument parsing, not follow it
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [api-design, error-handling]
---

Argument parsing exceptions (missing args, invalid choices) happen before error handlers and bypass JSON envelope. Move argument parsing after envelope setup or wrap it in a try-catch that emits JSON for all errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
