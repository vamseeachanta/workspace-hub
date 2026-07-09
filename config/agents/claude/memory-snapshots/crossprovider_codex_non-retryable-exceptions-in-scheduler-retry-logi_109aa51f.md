---
name: crossprovider codex non-retryable-exceptions-in-scheduler-retry-logi
description: Non-retryable exceptions in scheduler retry logic must be named explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler, error-handling, testing, determinism]
---

Prose like 'deterministic source error' is too vague for plan verification. Exception types must be imported and registered with the retry handler (e.g., `CoresSourceError`, `CoresParseError`). Tests must verify the exact exception class triggers non-retryable behavior, or false-green can hide real coverage gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
