---
name: crossprovider codex stacked-pr-chaining-for-sequential-publisher-pro
description: Stacked-PR chaining for sequential publisher processing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, stacked-prs, deduplication, dispatch_corpus_ingest]
---

Each publisher's branch builds from the previous publisher's branch (not origin/main) when --chain flag is used. This ensures dedupe-before-write sees prior publisher output and eliminates cross-branch duplicate conflicts that would otherwise require manual union resolution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
