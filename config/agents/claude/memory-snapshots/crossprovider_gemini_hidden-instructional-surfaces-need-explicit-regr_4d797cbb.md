---
name: crossprovider gemini hidden-instructional-surfaces-need-explicit-regr
description: Hidden instructional surfaces need explicit regression coverage
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, docs-governance, workspace-structure]
---

Stale references hide in non-top-level instructional files (`.claude/docs/`, `.gemini/**/*.md`) even when main docs are updated. Regression tests must explicitly enumerate these hidden surfaces by path glob, not assume top-level doc scans cover them.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
