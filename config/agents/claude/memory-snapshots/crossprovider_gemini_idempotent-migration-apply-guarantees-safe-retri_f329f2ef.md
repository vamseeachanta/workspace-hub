---
name: crossprovider gemini idempotent-migration-apply-guarantees-safe-retri
description: Idempotent migration apply guarantees safe retries
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, idempotence, retry-safety]
---

Migration scripts must guarantee idempotency: a second `--apply` run on unchanged state produces no content diff. This enables safe retries after partial failures or approval-stage rollbacks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
