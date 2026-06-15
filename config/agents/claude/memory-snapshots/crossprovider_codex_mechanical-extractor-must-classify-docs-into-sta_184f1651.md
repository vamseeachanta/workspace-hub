---
name: crossprovider codex mechanical-extractor-must-classify-docs-into-sta
description: Mechanical extractor must classify docs into standards, papers, and junk
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [extraction, routing, classification]
---

A deterministic extractor handling multiple namespaces needs `_is_standard()`, `_is_paper()`, and junk-marker logic. Split `PAPER_MARKERS` and `JUNK_MARKERS` separately. Route to namespace-specific directories (`standards/`, `papers/`, skip junk) with separate frontmatter logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
