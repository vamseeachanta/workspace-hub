---
name: crossprovider codex test-environment-dependency-isolation-and-error-
description: Test environment dependency isolation and error handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, security, secrets-handling]
---

Tests depending on ambient secrets or environment variables must fail explicitly with a clear missing-variable message, not leak the protected values in tracebacks or logs. Use fixture-based setup, not external state assumptions, so tests are reproducible without special shell setup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
