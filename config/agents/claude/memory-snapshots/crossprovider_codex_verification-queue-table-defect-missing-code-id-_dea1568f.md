---
name: crossprovider codex verification-queue-table-defect-missing-code-id-
description: Verification-queue table defect: missing code_id/table_id/source_page/parse_status columns
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [verification-queue, table-structure, parse-status, defect-pattern]
---

Tables written to verification queues MUST include metadata columns (code_id, table_id, source_pdf, source_page, parse_status) so verifiers can map rows back to source pages. Anonymous data rows with missing metadata make verification impossible and violate the hardened contract. This is a hard blocker caught in adversarial review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
