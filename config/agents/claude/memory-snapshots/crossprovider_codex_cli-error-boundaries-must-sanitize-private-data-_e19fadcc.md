---
name: crossprovider codex cli-error-boundaries-must-sanitize-private-data-
description: CLI error boundaries must sanitize private data in validation tracebacks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [security, cli, error-handling]
---

Jsonschema.ValidationError renders the complete rejected instance including paths and secrets. Must catch at boundary, emit sanitized error code only, and test that stderr contains no record content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
