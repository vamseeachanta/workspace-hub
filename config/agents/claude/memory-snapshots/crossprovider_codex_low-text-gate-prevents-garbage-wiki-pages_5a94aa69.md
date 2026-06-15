---
name: crossprovider codex low-text-gate-prevents-garbage-wiki-pages
description: Low-text gate prevents garbage wiki pages
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [extraction, quality-gate, content-filtering]
---

Gate on extractable word count (total_words < 200 or words_per_page < 10), not encrypted flag, to filter image-only scans and near-empty PDFs. Route these to vision queue instead of creating useless wiki pages. The encrypted flag alone is not reliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
