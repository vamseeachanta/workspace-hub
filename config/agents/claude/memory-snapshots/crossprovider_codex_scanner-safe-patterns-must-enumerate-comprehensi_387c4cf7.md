---
name: crossprovider codex scanner-safe-patterns-must-enumerate-comprehensi
description: Scanner-safe patterns must enumerate comprehensive substrings, not just exact matches
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, pattern-matching, testing, validation]
---

Banning a single pattern string (e.g., 'authority') leaves similar substrings undetected (e.g., 'auth', 'authorization'). Both guard patterns and test coverage must explicitly enumerate all dangerous substrings, and verify them independently—a guard that omits substrings will pass tests that also omit them, masking the defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
