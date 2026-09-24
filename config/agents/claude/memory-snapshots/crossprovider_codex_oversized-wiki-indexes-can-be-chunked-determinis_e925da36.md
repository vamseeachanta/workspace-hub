---
name: crossprovider codex oversized-wiki-indexes-can-be-chunked-determinis
description: Oversized wiki indexes can be chunked deterministically with idempotent scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wiki-pagination, chunking-strategy, idempotency]
---

Indexes >15K lines (e.g., marine-engineering 21K lines) chunk reproducibly into ~500-line bounded pages with prev/next/jump navigation. Chunker must normalize misplaced rows (source entries that leak past section boundaries), preserve YAML frontmatter, and be idempotent—re-running from generated chunk pages yields identical output, verified via checksums.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
