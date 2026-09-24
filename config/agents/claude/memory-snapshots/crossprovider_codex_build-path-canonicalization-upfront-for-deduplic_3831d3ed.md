---
name: crossprovider codex build-path-canonicalization-upfront-for-deduplic
description: Build path-canonicalization upfront for deduplicated extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [corpus-extraction, deduplication, path-handling]
---

Large corpus extraction with work-in-progress prefixes, dated transmittal folders, and historical revisions requires deduplication logic built upfront. Without path-canonicalization (removing Old/, dated prefixes, resolving folder variants), the extracted content duplicates and breaks downstream processing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
