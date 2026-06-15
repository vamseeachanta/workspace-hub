---
name: crossprovider codex page-size-splitting-threshold-120-kb-per-page
description: Page size splitting threshold: 120 KB per page
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [page-sizing, chunking, extraction]
---

If a single page extraction would exceed ~120 KB, split into sub-pages (or use scripts/wiki/chunk_wiki_index.py) rather than truncating. Keeps wiki pages navigable and avoids silent data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
