---
name: crossprovider codex markdown-parsing-scope-boundaries-must-be-explic
description: Markdown parsing scope boundaries must be explicit in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parsing-robustness, scope-definition, forward-safety]
---

When implementing markdown checks, document what is out of scope (e.g., Setext headings, BOM, inline HTML comments, duplicate sections) in the acceptance criteria, not left implicit. Otherwise implementations diverge and false positives accumulate as README variations appear over time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
