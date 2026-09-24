---
name: crossprovider codex environment-validation-must-abort-not-degrade
description: Environment validation must abort, not degrade
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, environment-validation, migration-safety]
---

Unsupported environments should exit non-zero with explicit `UNSUPPORTED_ENV_ABORT` status before any mutation, rather than allowing partial/unclear failures. Fail-fast prevents audit gaps and rollback ambiguity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
