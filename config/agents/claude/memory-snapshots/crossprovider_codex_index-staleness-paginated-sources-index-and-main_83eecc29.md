---
name: crossprovider codex index-staleness-paginated-sources-index-and-main
description: Index staleness: paginated sources-index and main index.md diverge after augmentation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [index-maintenance, ingest-hazard, staleness]
---

When a page is augmented and retitled, the main index.md reflects the new title and date, but the paginated sources-index/sources-NNN.md view can become stale (old title, old summary, old date). These are separate surfaces that don't auto-sync; after any augmentation, manually update the paginated index entry to match.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
