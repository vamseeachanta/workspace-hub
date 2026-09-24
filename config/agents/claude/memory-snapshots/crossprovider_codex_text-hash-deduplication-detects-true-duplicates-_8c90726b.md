---
name: crossprovider codex text-hash-deduplication-detects-true-duplicates-
description: Text-hash deduplication detects true duplicates despite metadata differences
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, content-hash, variant-detection]
---

Files with different names/metadata can contain identical content. Use SHA256 of full extracted text to detect true duplicates, not filename or metadata comparison alone. This catches draft/edition/lineage variants that would otherwise create false duplicates or split canonical entries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
