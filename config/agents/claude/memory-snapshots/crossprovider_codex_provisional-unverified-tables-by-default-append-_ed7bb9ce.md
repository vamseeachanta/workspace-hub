---
name: crossprovider codex provisional-unverified-tables-by-default-append-
description: Provisional-unverified tables by default—append to domain verification queue
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [table-extraction, verification-workflow, data-quality]
---

Page-level parse_status and all extracted tables marked provisional-unverified or raw-unverified on first ingest; never marked verified. Tables added to domain's datasets/_verification-queue.csv (columns: code_id, table_id, source_pdf, source_page, parse_status, caption). Verification happens in separate pass by domain experts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
