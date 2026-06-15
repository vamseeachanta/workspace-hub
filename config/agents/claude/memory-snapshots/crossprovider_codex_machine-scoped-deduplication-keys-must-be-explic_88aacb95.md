---
name: crossprovider codex machine-scoped-deduplication-keys-must-be-explic
description: Machine-scoped deduplication keys must be explicit in idempotency contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [distributed-systems, idempotency, contract]
---

Cross-machine state deduplication (e.g., 'no double-dispatch across machines') requires the idempotency key to be explicit about machine scope. Plan specifying 'issue:provider' while code uses 'issue:provider:machine' creates split-brain risk without being obvious. Always state: is idempotency per-machine, per-cluster, or global? Make the key-scoping visible in acceptance criteria and test fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
