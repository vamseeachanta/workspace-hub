---
name: crossprovider codex dedupe-before-write-is-a-mandatory-contract-to-p
description: Dedupe-before-write is a mandatory contract to prevent duplicate entries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest-contract, deduplication, data-pipeline]
---

Before creating or augmenting any entry (wiki page, dataset, etc.), search the target domain/collection for existing entries by code/ID/title. If found, augment in place rather than creating a duplicate. This pattern is load-bearing in large ingest pipelines and prevents silent duplicates from accumulating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
