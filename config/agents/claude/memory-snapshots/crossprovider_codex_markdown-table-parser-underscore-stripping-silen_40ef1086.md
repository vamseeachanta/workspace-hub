---
name: crossprovider codex markdown-table-parser-underscore-stripping-silen
description: Markdown table parser underscore stripping silently corrupts field names
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [markdown, parser, silent-corruption, llm-wiki#23]
---

llm-wiki #23 validator: markdown-cell cleanup stripped underscores, turning `doc_key` → `dockey`, `last_updated` → `lastupdated`. Silent defect if tests expect the corrupted output. Pattern: markdown table extraction must preserve field-name structure; validate round-trip.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
