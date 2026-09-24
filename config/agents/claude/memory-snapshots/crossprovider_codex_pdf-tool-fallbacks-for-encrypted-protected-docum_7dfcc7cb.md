---
name: crossprovider codex pdf-tool-fallbacks-for-encrypted-protected-docum
description: PDF tool fallbacks for encrypted/protected documents
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-tools, encryption-handling, tooling-quirks]
---

pdfinfo works on most encrypted PDFs; Poppler (pdftotext) fails on FOPN-protected files. Workaround: extract raw PDF page-tree structure via sed/grep on the binary to recover page counts when tools fail. Useful for inventory/classification even when full text extraction is blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
