---
name: crossprovider codex ntfs-surrogate-character-handling-in-drive-index
description: NTFS surrogate character handling in drive indexing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [drive-indexing, sqlite, ntfs, batch-fallback]
---

Walk with `errors='surrogateescape'` to capture undecodable filenames, then sanitize TEXT columns before SQLite storage. When an executemany batch fails due to surrogates, fall back to per-row inserts and skip the failed row with a warning. This pattern handles real filesystem edge cases without blocking the entire scan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
