---
name: crossprovider codex large-pdfs-300-pages-split-by-section-with-manif
description: Large PDFs (300+ pages) split by section with manifest
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [large-documents, chunking, scalability]
---

Standards exceeding ~120 KB per page are split into sub-pages (Scope, Definitions, Requirements, Tables, Methodology) with a manifest/index page linking sections. This prevents truncation, keeps pages navigable, and allows independent verification of parts. Use scripts/wiki/chunk_wiki_index.py for automated splitting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
