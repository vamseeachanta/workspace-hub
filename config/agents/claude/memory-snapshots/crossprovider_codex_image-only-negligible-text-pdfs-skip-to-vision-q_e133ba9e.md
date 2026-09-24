---
name: crossprovider codex image-only-negligible-text-pdfs-skip-to-vision-q
description: Image-only/negligible-text PDFs skip to vision queue
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [content-filter, vision-queue, quality-gate]
---

Scanned documents or image-heavy PDFs with <~4 KB extractable text do not become wiki pages; add them to _skipped.csv with reason and tag for issue #135 vision queue. Prevents garbage/near-empty pages that clutter the knowledge base. Requires active OCR or manual inspection before ingest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
