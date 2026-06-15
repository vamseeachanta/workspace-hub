---
name: crossprovider codex frontmatter-parsing-breaks-on-nested-yaml-struct
description: Frontmatter parsing breaks on nested YAML structures
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [parser-fragility, wiki-design, metadata-structure]
---

Simple frontmatter parsers (used in graph/search generators) fail on nested YAML. Complex metadata inventory belongs in body tables with clear structure, not frontmatter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
