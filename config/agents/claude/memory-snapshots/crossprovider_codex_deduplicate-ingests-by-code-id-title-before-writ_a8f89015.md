---
name: crossprovider codex deduplicate-ingests-by-code-id-title-before-writ
description: Deduplicate ingests by code_id + title before writing new pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, deduplication, wiki, standards]
---

Before creating a new standards page or wiki entry during an ingest, grep the target domain's `standards/` and `sources/` directories for an existing page with the same `code_id` and title. If found, augment in place (add missing sections/tables) rather than creating a duplicate entry.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
