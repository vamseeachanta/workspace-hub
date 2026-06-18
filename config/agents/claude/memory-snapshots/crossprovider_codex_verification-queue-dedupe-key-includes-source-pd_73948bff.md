---
name: crossprovider codex verification-queue-dedupe-key-includes-source-pd
description: Verification queue dedupe key includes source_pdf
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [llm-wiki, deduplication, verification-queue, provenance]
---

In llm-wiki, duplicate-row detection uses csv_path + page + source_pdf. Provenance backfill that doesn't preserve source_pdf group-consistency can inadvertently split or merge duplicate identities, requiring re-dedup. This is a TDD insertion point for issue #291.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
