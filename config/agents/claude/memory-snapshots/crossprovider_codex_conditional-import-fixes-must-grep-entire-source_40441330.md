---
name: crossprovider codex conditional-import-fixes-must-grep-entire-source
description: Conditional import fixes must grep entire source tree first
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, imports, ci-correctness]
---

When fixing optional-dependency imports (e.g., making seaborn lazy to handle missing [viz] extra), grep the entire src/ tree before implementing. Single-file fixes that miss sibling import sites cause CI failures downstream. Document the sites found and verify each is addressed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
