---
name: crossprovider codex ast-walk-traverses-all-nested-scopes-not-module-
description: ast.walk() traverses all nested scopes, not module level only
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python-ast, code-auditing, correctness]
---

Python's `ast.walk(tree)` recursively visits every node in the tree, including nested functions, methods, and closures. To count only top-level module/class symbols, use explicit traversal of `tree.body` and `ClassDef.body` instead. This matters for code audits and coverage metrics because walk() will overcount symbols if inner functions are present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
