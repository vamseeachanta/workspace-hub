---
name: crossprovider codex composite-keys-for-multi-account-state-tracking
description: Composite keys for multi-account state tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-tenant, schema-design, correctness]
---

When adding state-tracking or identity-based features to multi-account systems, use composite primary keys everywhere: JSONL schemas, database records, test fixtures, pseudocode, and idempotency rules. Example: `(account_id, thread_id)` prevents silent cross-account collisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
