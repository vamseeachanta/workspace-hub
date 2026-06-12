---
name: crossprovider codex image-only-pdfs-metadata-only-stub-vision-queue-
description: Image-only PDFs: metadata-only stub + vision-queue, never empty page
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [image-only, metadata-only, vision-queue, pdf-inspection]
---

Native pdftotext on image-only returns form-feeds. Create metadata-only stub (code_id, publisher, revision, license_status) and add to vision queue instead. Use pdfimages/OCR to classify before deciding to skip or stub.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
