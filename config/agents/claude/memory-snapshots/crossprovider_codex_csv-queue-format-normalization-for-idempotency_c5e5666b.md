---
name: crossprovider codex csv-queue-format-normalization-for-idempotency
description: CSV queue format normalization for idempotency
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [csv, queue, idempotency, data-format]
---

Older queue rows use 6-col named format (code_id, table_id, source_pdf, source_page, parse_status, caption); newer provisional rows are 4-col positional (parse_status, code_id, page, csv_path). Verifier must normalize both shapes or idempotent re-runs corrupt the queue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
