---
name: crossprovider hermes dual-parsing-wikilink-and-markdown-links-in-same
description: Dual-parsing wikilink and markdown links in same text creates phantom edge explosion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parsing, link-extraction, data-generation, schema-pollution, llm-wiki]
---

Processing `[[label]](target.md)` through both wikilink parser (`[[label]]` → .pdf anchor) and markdown link parser independently emits spurious unresolved edges to non-existent targets. In llm-wiki #77: 17,488 false edges from `wikis/marine-engineering/wiki/index.md`. Prevention: parse in order (markdown before wikilink if label is URL) or deduplicate by final target.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
