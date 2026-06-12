---
name: crossprovider codex image-only-pdfs-go-to-skipped-csv-not-pages
description: Image-only PDFs go to _skipped.csv, not pages
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [content-quality, ingest-filtering, vision-queue]
---

PDFs with negligible extractable text (image-only scans, drawings) should not become pages. Add them to _skipped.csv with a reason and flag to the #135 vision queue. Prevents garbage/near-empty pages from polluting the wiki.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
