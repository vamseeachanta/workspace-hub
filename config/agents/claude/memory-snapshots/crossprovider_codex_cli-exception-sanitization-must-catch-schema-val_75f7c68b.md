---
name: crossprovider codex cli-exception-sanitization-must-catch-schema-val
description: CLI exception sanitization must catch schema-validation errors, not just record-validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [cli-security, exception-handling, output-sanitization]
---

When catching exceptions at a CLI boundary for output sanitization (to prevent leaking internal structure or sensitive values), include schema-validation exceptions (e.g., `jsonschema.SchemaError`) alongside record-validation errors. User-selectable `--schema` flags can trigger unsanitized tracebacks if schema errors are not caught and converted to stable error messages. Regression tests should verify exact exit codes and absence of sentinel strings in stderr.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
