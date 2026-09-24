---
name: crossprovider gemini guard-conditions-protect-idempotent-operations-f
description: Guard conditions protect idempotent operations from cascading corruption
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [idempotency, design-contracts, safety]
---

An operation claiming to be idempotent (safe to re-run) must detect already-completed work and skip or abort cleanly. For example, 'feature already has children → abort' prevents new-feature.sh from creating duplicates if re-invoked. Guard checks are not optional.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
