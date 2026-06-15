---
name: crossprovider codex idempotent-data-rewrites-with-write-gates
description: Idempotent data rewrites with write gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [idempotency, data-integrity, optimization]
---

Only write the CSV if processing changed rows or dedup found duplicates. Re-run with zero changes must yield process=0 dedup=0 to prove idempotency and prevent file churn.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
