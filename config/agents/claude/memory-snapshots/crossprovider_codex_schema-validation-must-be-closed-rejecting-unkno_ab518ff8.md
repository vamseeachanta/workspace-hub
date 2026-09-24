---
name: crossprovider codex schema-validation-must-be-closed-rejecting-unkno
description: Schema validation must be closed, rejecting unknown keys
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, schema-design, configuration]
---

Config schemas that allow arbitrary JSON keys bypass allowlist intent. A schema allowing `rules: [{pattern: ...}]` can still accept `rules: [{client_names: [...], pattern: ...}]` with real identifiers in the unknown field. Use JSON Schema `additionalProperties: false` or equivalent to reject unknown keys; don't rely on string-matching alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
