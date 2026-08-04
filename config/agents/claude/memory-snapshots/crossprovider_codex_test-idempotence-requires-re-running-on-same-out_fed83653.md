---
name: crossprovider codex test-idempotence-requires-re-running-on-same-out
description: Test idempotence requires re-running on same output
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, idempotence, regression]
---

Tests that run transformations on fresh temp state each time prove repeatability, not idempotence. Durable test: save first output → apply transform again to that same output → assert byte identity. Session 8 found new fixtures proven green only via repeatability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
