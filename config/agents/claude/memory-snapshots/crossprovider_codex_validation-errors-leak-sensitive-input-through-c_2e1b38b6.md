---
name: crossprovider codex validation-errors-leak-sensitive-input-through-c
description: Validation errors leak sensitive input through CI artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [security, logging, data-privacy]
---

Error messages that interpolate untrusted input (rejected records, config values, source identifiers) escape through CI logs and copied tracebacks into public artifacts. Use generic error text with only safe identifiers (code IDs, ranks); never interpolate the actual rejected value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
