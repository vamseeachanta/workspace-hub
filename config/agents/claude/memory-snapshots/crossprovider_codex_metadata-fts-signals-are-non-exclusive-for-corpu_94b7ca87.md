---
name: crossprovider codex metadata-fts-signals-are-non-exclusive-for-corpu
description: Metadata FTS signals are non-exclusive for corpus classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-classification, metadata, canary-queue]
---

Full-text search signals derived from filenames and paths (e.g., 90.3% manufacturing hits) are non-exclusive metadata indicators, not validated content classification. Require content hashing or human review canary before partitioning on metadata-only signals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
