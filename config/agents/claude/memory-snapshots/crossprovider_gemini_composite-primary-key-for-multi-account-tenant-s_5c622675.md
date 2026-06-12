---
name: crossprovider gemini composite-primary-key-for-multi-account-tenant-s
description: Composite primary key for multi-account/tenant scenarios
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-design, multi-tenant, schema-design]
---

Design state schemas with composite keys (e.g., account_id + thread_id, not thread_id alone) even for single-tenant v1. Discovered late in adversarial review when assumed 'single account' was unstated; composite is cheap upfront, expensive to retrofit. Prevents cross-account data collisions when system scales.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
