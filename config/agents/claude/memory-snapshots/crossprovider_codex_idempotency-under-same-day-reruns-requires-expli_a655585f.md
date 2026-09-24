---
name: crossprovider codex idempotency-under-same-day-reruns-requires-expli
description: Idempotency under same-day reruns requires explicit replace-by-key semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, idempotency, data-integrity]
---

Deduplication by (event, provider, date) fails when a run is corrected and rerun the same day. The updated record is discarded as a duplicate. Plan must specify replace-by-key semantics (e.g., rewrite the day file with latest records by key, or add a run/version field with latest-wins logic). Without this, bad runs cannot be corrected mid-day.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
