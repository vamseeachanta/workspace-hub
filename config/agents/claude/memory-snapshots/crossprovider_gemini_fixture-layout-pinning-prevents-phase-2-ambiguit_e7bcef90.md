---
name: crossprovider gemini fixture-layout-pinning-prevents-phase-2-ambiguit
description: Fixture layout pinning prevents Phase 2 ambiguity
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tdd, testing, fixtures]
---

Specify exact fixture structure (directory layout, file paths, frontmatter schema) in Phase 1 before any implementation. Avoid "adjust if needed" framing—any layout changes require fixture-first updates. Prevents surprises when tests try to use fixtures that don't match the implementation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
