---
name: crossprovider codex bulk-cleanup-requires-per-item-verification-not-
description: Bulk cleanup requires per-item verification, not pattern-based deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cleanup, operational, data-loss-prevention]
---

Cleaning up 100+ items with rules like 'age > 30 days' or 'matches pattern' risks losing data. Each item needs verification: origin status, dirty/untracked state, active process references, and residue type. Active sessions, linked files, and stashed work are easy to miss at scale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
