---
name: crossprovider codex markdown-cell-parser-strips-underscores-in-field
description: Markdown cell parser strips underscores in field names
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [markdown-parsing, llm-wiki, frontmatter-extraction]
---

When parsing markdown table cells, underscore characters can be accidentally stripped during cleanup (e.g., `doc_key` becomes `dockey`, `last_updated` becomes `lastupdated`). Validators parsing schema frontmatter from markdown must handle or preserve special characters explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
