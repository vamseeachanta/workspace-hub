---
name: crossprovider codex ast-walk-traverses-nested-scopes-not-just-module
description: ast.walk() traverses nested scopes, not just module-level symbols
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-ast, api-audit, correctness]
---

Using `ast.walk(tree)` to audit public API coverage will include nested functions, local helpers, and nested classes defined inside other scopes. Public-only symbol collection requires explicit traversal of `tree.body` and `ClassDef.body` to avoid false counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
