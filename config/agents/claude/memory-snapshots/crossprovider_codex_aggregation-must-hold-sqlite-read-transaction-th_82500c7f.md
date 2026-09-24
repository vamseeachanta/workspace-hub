---
name: crossprovider codex aggregation-must-hold-sqlite-read-transaction-th
description: Aggregation must hold SQLite read transaction through counting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sqlite, concurrency, aggregation, transaction]
---

When aggregating ledger entries, hold the SQLite read transaction from ledger verification through result counting to ensure atomicity. Releasing the lock between verification and count allows concurrent mutations to corrupt the aggregate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
