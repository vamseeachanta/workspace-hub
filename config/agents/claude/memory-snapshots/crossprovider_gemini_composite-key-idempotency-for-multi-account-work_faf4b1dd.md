---
name: crossprovider gemini composite-key-idempotency-for-multi-account-work
description: Composite-key idempotency for multi-account workflows
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [composite-key, idempotency, multi-account]
---

Use `(account_id, thread_id)` as primary key throughout fixtures, schema, and pseudocode. Make ownership split explicit in the dependency matrix when work spans issues to avoid identity collisions at scale.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
