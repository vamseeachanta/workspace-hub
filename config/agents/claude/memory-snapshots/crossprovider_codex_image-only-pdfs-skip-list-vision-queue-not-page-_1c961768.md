---
name: crossprovider codex image-only-pdfs-skip-list-vision-queue-not-page-
description: Image-only PDFs → skip list + vision queue, not page stubs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [content-filtering, image-only, vision-queue, llm-wiki]
---

PDFs with negligible extractable text (scanned documents, drawings) should be added to a `_skipped.csv` with reason and queued to the #135 vision OCR backlog. Never create empty or nearly-empty page stubs to avoid polluting the index.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
