---
name: crossprovider codex verification-queue-discipline-provisional-by-def
description: Verification Queue Discipline: Provisional-by-Default Tables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [table-quality, verification-queue, parse-status]
---

Every parsed/extracted table gets parse_status provisional-unverified (clean structure) or raw-unverified (merged cells, uncertain columns). Never auto-mark verified by extraction automation. Append all provisional/raw tables to <domain>/wiki/datasets/_verification-queue.csv for later human/vision review. This prevents false confidence in automated extraction and preserves quality gates for large corpus ingests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
