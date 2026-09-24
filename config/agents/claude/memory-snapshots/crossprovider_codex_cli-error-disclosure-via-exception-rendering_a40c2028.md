---
name: crossprovider codex cli-error-disclosure-via-exception-rendering
description: CLI error disclosure via exception rendering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, error-handling, testing]
---

Unhandled `jsonschema.ValidationError` renders the full rejected instance including private data (paths, identifiers, content snippets) to stderr. Must catch at CLI boundary and emit sanitized error codes/messages without disclosing record values. Regression-test via /dev/stdin with private-path sentinel.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
