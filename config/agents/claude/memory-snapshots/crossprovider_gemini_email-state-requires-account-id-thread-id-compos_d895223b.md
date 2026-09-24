---
name: crossprovider gemini email-state-requires-account-id-thread-id-compos
description: Email state requires (account_id, thread_id) composite key everywhere
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [email, data-modeling]
---

Multi-account email state tracking needs composite primary key applied to JSONL, snapshot, fixtures, schemas, idempotency rules. Single-account assumptions surface as P1 findings in adversarial review.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
