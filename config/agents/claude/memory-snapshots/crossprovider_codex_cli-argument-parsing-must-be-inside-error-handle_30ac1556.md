---
name: crossprovider codex cli-argument-parsing-must-be-inside-error-handle
description: CLI argument parsing must be inside error handlers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [error-handling, cli, safety, user-input]
---

User input parsing (e.g., `--water-depth` from click) outside the try-catch escapes the formatted error path, raising raw ValueError instead. Move all input parsing into the error-handling block.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
