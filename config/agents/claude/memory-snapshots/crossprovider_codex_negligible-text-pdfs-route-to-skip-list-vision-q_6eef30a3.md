---
name: crossprovider codex negligible-text-pdfs-route-to-skip-list-vision-q
description: Negligible-text PDFs route to skip list + vision queue, not empty pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-ingest, skip-logic, vision-queue]
---

Image-only or heavily scanned PDFs with <~100 extractable characters should be added to a `_skipped.csv` manifest and queued for vision pipeline review, not ingested as near-empty wiki pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
