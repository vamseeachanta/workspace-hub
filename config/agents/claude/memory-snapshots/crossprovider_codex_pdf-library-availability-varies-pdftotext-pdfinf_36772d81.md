---
name: crossprovider codex pdf-library-availability-varies-pdftotext-pdfinf
description: PDF library availability varies; pdftotext/pdfinfo reliable, pdfplumber sparse
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf-tools, environment-quirk, fallback-patterns]
---

pdftotext, pdfinfo, pdfimages (Poppler tools) work across environments. pdfplumber often unavailable in temporary worktrees. When pdfplumber unavailable, fall back to pdftotext + manual character-count + pdfimages inspection for table inventory. Some PDFs have unsupported security handlers (FOPN_foweb) → pdfinfo works, pdftotext fails → metadata-only route.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
