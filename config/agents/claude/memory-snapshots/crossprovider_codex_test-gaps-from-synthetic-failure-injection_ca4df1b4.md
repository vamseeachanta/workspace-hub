---
name: crossprovider codex test-gaps-from-synthetic-failure-injection
description: Test gaps from synthetic failure injection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, test-coverage, security]
---

Tests using synthetic post-operation failure injection can false-green on descriptor leaks or stage-tracking defects. Exercise real primitive failures (mkdir, open, fstat, chmod, write) by mocking the OS layer, not application code. Prove cleanup/rollback for every failure stage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
