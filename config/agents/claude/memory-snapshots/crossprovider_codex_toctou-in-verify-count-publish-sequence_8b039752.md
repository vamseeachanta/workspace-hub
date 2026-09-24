---
name: crossprovider codex toctou-in-verify-count-publish-sequence
description: TOCTOU in verify-count-publish sequence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, toctou, ledger, atomicity]
---

When code authenticates ledger state, releases that view, performs independent count, then signs checkpoint values based on stale verification, concurrent mutations during the count phase are accepted. Solution: hold write-reserving transaction (BEGIN IMMEDIATE) from fresh re-verification through result derivation and coverage publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
