---
name: crossprovider codex new-wiki-content-and-structured-outputs-require-
description: New wiki content and structured outputs require explicit frontmatter/metadata schema
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, wiki-contracts, metadata]
---

Plans creating wiki pages, YAML outputs, or markdown summaries must specify required frontmatter fields (title, last_updated, doc_key, etc.) and metadata contract upfront. Leaving this to 'test verification' leaves downstream consumers (indexers, promoters) without a durable contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
