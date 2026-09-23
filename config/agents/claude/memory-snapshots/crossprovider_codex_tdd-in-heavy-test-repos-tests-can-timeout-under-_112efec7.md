---
name: crossprovider codex tdd-in-heavy-test-repos-tests-can-timeout-under-
description: TDD in heavy-test repos: tests can timeout under load
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [testing, performance, concurrency]
---

Test collection and import can hang for 60–180 seconds under filesystem contention from parallel sibling processes. Incomplete test runs are not evidence of code failure; use bounded runs and independent re-derivation when timeouts occur.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
