---
name: crossprovider codex dedupe-search-by-content-not-hash-duplicates-hav
description: Dedupe search by content, not hash—duplicates have identical text but different SHA-256
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [deduplication, pdf-metadata, workflow-edge-case]
---

Multiple instances of the same PDF (e.g., OTC-25134-MS appears twice in OnePetro folder) have identical extracted title and word count but different file hashes due to metadata/modification timestamps. Use content-based deduping (grep for code_id+title in target domain, exact title match) not file hash comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
