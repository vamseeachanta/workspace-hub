---
name: crossprovider codex validator-status-enumeration-must-be-exhaustive
description: Validator status enumeration must be exhaustive
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [validation, error-handling, fail-closed]
---

Validators that exit with specific status codes (e.g., 0/2/3/4 for different failures) need explicit handlers for *unexpected* statuses, else odd exit codes fall through to pass logic. Session 3 found a semantic validator returning status 7 still allowed strict mode to exit zero.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
