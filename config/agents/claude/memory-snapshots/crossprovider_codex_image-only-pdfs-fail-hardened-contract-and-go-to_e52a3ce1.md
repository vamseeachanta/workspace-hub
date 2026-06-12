---
name: crossprovider codex image-only-pdfs-fail-hardened-contract-and-go-to
description: Image-only PDFs fail hardened contract and go to vision queue
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-ingest, hardened-contract, image-only]
---

Scanned PDFs with negligible embedded text (pdftotext yields ~0 chars) cannot be ingested as pages; they are rejected at content-value filter. Route to skip list and #135 vision queue only. No workaround within hardened-contract scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
