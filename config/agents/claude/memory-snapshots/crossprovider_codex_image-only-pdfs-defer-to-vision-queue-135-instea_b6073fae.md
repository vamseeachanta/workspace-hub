---
name: crossprovider codex image-only-pdfs-defer-to-vision-queue-135-instea
description: Image-only PDFs defer to vision queue #135 instead of creating pages
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [content-filtering, image-processing, issue-#135]
---

ABS guides, old scans with negligible extractable text (< 1000 words or drawing-only) never become wiki pages. Instead: add to domain's _skipped.csv (filename, reason) and enqueue in GitHub issue #135 for vision-based processing. This prevents garbage page accumulation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
