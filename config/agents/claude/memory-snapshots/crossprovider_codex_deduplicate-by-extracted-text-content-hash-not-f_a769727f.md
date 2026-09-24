---
name: crossprovider codex deduplicate-by-extracted-text-content-hash-not-f
description: Deduplicate by extracted-text content hash, not filename or code_id
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dedupe, content-hash, deduplication]
---

Multiple PDF files for the same standard may have identical extracted-text SHA256 but different file SHA256 and filenames. Use text-content hash to identify true duplicates; augment existing pages rather than create new ones. Example: ISO-DIS-19901-1 variants with identical extracted text but different filenames.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
