---
name: crossprovider gemini composite-primary-key-for-multi-tenant-state-tra
description: Composite primary key for multi-tenant state tracking
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-modeling, multi-tenant, idempotency, state-machines]
---

When tracking thread state across multiple email accounts, use (account_id, thread_id) as composite primary key everywhere: JSONL logs, snapshots, fixtures, pseudocode, and schema. This was a critical P1 finding in the #2017 email-queue plan that required rewrite.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
