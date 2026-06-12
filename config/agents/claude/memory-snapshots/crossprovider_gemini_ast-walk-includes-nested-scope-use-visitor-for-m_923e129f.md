---
name: crossprovider gemini ast-walk-includes-nested-scope-use-visitor-for-m
description: AST.walk() includes nested scope; use visitor for module/class-level only
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ast, python, code-analysis]
---

ast.walk() traverses the entire tree recursively, yielding nested functions as if they were module-level. For module/class-level symbol collection, use ast.NodeVisitor with filtered traversal, or filter results by parent scope. Replace custom has_docstring() with ast.get_docstring().

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
