---
name: crossprovider codex cached-state-tests-must-verify-the-cache-is-cons
description: Cached-state tests must verify the cache is consulted
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, correctness, caching]
---

Tests of code that computes and caches state often verify only the final output, missing double-computation and cache-miss bugs. Add tests that spy on cache behavior: verify the cache is actually consulted on repeat calls, that computation happens exactly once, and that stale-cache scenarios are caught. Output-only tests are insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
