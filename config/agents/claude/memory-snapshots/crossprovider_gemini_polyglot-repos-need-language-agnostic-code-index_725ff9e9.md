---
name: crossprovider gemini polyglot-repos-need-language-agnostic-code-index
description: Polyglot repos need language-agnostic code indexing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [polyglot, indexing, ast, search]
---

A Python-only AST walker for symbol indexing misses JS/TS and other languages. In polyglot environments, use language-agnostic tools (ctags, tree-sitter, ripgrep) or explicitly support multiple parsers. Incomplete indexing degrades search value.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
