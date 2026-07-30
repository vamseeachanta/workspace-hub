---
name: crossprovider codex ntfs-cross-filesystem-walks-surrogateescape-sani
description: NTFS cross-filesystem walks: surrogateescape + sanitize before storage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [implementation, data-integrity]
---

When walking NTFS filesystems mixed into Unix paths, use `walk(errors='surrogateescape')` to capture undecodable filenames, then sanitize TEXT fields before sqlite3 storage—sqlite rejects surrogates. When a batch insert fails on undecodable names, fall back to per-row inserts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
