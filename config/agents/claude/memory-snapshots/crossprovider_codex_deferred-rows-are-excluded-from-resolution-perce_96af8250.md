---
name: crossprovider codex deferred-rows-are-excluded-from-resolution-perce
description: Deferred rows are excluded from resolution percentage per convention
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [aggregation, project-convention, index-semantics]
---

Project convention: `pct_resolved = (verified + rejected) / total_tables`, excluding deferred rows from both numerator and denominator. Check repository precedent (prior index rows with deferred statuses) before rebuilding aggregates or flagging staleness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
