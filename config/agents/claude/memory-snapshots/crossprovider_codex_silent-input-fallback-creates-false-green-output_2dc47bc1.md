---
name: crossprovider codex silent-input-fallback-creates-false-green-output
description: Silent input fallback creates false-green output
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, error-handling, cli-design]
---

Domain mapping, flag validation, or default selection that silently accepts invalid input and falls back to generic/default (e.g. domain typo → generic template, both --ruff-only and --mypy-only → skip both checks and exit 0) produces incorrect output while exiting success. Validate early and reject unknown inputs explicitly, printing allowed values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
