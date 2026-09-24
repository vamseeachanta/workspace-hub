---
name: crossprovider codex non-retryable-error-classification-must-name-con
description: Non-retryable error classification must name concrete exception types
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, scheduler-retry, specification-precision]
---

Vague language like 'deterministic error' in specs allows implementations to use wrong exception types. Concrete exception names must be used in plan/implementation/test artifacts so reviewers can verify the correct exception is imported and classified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
