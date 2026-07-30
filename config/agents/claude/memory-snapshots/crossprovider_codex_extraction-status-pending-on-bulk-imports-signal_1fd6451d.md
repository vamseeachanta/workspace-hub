---
name: crossprovider codex extraction-status-pending-on-bulk-imports-signal
description: Extraction_status=pending on bulk imports signals incomplete validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [data-quality, bulk-ingest, validation]
---

When 1.3M indexed rows all have extraction_status=pending, the content extraction or validation phase was skipped or failed. Verify actual extraction ran before treating metadata as authoritative.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
