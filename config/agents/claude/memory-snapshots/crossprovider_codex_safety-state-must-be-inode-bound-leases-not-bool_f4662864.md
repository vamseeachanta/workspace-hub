---
name: crossprovider codex safety-state-must-be-inode-bound-leases-not-bool
description: Safety state must be inode-bound leases, not booleans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, design-pattern, safety]
---

Representing safety/lock state as names or booleans is insufficient. Use inode-bound leases that can be verified, reclaimed, and checked for staleness. This is a correctness boundary found through multi-round review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
