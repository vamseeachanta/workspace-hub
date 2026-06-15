---
name: crossprovider codex dedupe-by-code-id-title-augment-existing-pages-n
description: Dedupe by code_id + title; augment existing pages, never duplicate
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [deduplication, page-management, content-consolidation]
---

Before creating a standards page, grep the target domain for an existing page on the same standard (code_id + title match). If found, augment in place with missing sections/tables rather than overwrite wholesale or create a duplicate. Source-variant duplicates (same standard, different PDFs) are augmentation opportunities, not separate pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
