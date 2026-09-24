---
name: crossprovider gemini line-by-line-regex-parsing-misses-yaml-block-sty
description: Line-by-line regex parsing misses YAML block-style values
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml, parsing, frontmatter]
---

Simple regex like `rf"^{field}:[ \t]*(.*)$"` only captures inline values, failing silently on block-style YAML (multi-line lists). When parsing frontmatter, validate that critical fields are present, or use a proper YAML parser.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
