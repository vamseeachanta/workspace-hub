---
name: crossprovider codex folder-labels-unreliable-for-ingest-routing
description: Folder labels unreliable for ingest routing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [ingest-routing, content-analysis, misfiled, dedupe]
---

ISO and API folders contain misclassified content (personal/legal docs, out-of-scope PDFs). Route each document by actual content analysis (PDF metadata, title, text extraction), not folder hierarchy. Prevents misfiled pages and duplicates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
