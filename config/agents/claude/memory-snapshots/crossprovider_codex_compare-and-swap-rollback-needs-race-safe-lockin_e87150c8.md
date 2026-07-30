---
name: crossprovider codex compare-and-swap-rollback-needs-race-safe-lockin
description: Compare-and-swap rollback needs race-safe locking throughout transaction
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [concurrency, transactions]
---

Write and rollback phases must hold the same lock from baseline snapshot through backup, write, and verification. Unlocked rollback can race with concurrent mutations, leaving the system in an inconsistent state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
