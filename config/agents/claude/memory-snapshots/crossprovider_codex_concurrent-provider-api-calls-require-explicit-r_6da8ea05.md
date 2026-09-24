---
name: crossprovider codex concurrent-provider-api-calls-require-explicit-r
description: Concurrent provider API calls require explicit rate-limit handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [providers, concurrency, rate-limiting, error-handling]
---

Launching 9+ concurrent API calls to providers triggers quota exhaustion and failures. Explicit retry logic, exponential backoff, and degraded-mode synthesis (handling partial results) are mandatory for concurrent orchestration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
