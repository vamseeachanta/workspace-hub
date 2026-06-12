---
name: crossprovider gemini symbol-indexing-needs-language-support-beyond-py
description: Symbol indexing needs language support beyond Python
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [indexing, polyglot, architecture]
---

AST walkers that only parse Python miss JS/TS and other languages in polyglot codebases. Use ctags, tree-sitter, or add explicit parsers per language; Python-only indexing is incomplete for cross-repo symbol search (WRK-1085).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
