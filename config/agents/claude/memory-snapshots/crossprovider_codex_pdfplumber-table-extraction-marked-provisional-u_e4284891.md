---
name: crossprovider codex pdfplumber-table-extraction-marked-provisional-u
description: Pdfplumber table extraction marked provisional-unverified
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdfplumber, parse-status, tables, verification-queue]
---

Tables extracted via pdfplumber are marked `parse_status: provisional-unverified` in frontmatter because automated extraction cannot guarantee fidelity. Raw layout captures marked `raw-unverified`. Append rows to domain's `_verification-queue.csv` for manual review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
