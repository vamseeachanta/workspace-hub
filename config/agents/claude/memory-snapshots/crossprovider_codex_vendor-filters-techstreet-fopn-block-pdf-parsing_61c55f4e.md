---
name: crossprovider codex vendor-filters-techstreet-fopn-block-pdf-parsing
description: Vendor filters (Techstreet, FOPN) block PDF parsing—defer to vision queue
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-parsing, vendor-drm, vision-queue]
---

Some PDFs like 6D_AnnexF.pdf have custom content filters (Techstreet/FOPN) that prevent opening by standard PDF parsers (pdfinfo, pdftotext, pdfplumber all fail). Add to _skipped.csv and defer to vision queue #135 instead of manual extraction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
