---
name: crossprovider codex markdown-parser-silently-transforms-underscore-f
description: Markdown parser silently transforms underscore field names
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [parser, markdown, schema]
---

Markdown-to-dict converters may transform field names (e.g., `doc_key` → `dockey`, `last_updated` → `lastupdated`). Test parser output against expected field names before writing schema validators; mismatches cause silent contract failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
