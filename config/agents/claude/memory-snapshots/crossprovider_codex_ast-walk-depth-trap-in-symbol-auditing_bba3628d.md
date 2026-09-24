---
name: crossprovider codex ast-walk-depth-trap-in-symbol-auditing
description: AST walk depth trap in symbol auditing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ast, python, auditing, correctness]
---

`ast.walk()` traverses all nested functions and scopes, not just module-level definitions. To audit only top-level symbols and class methods, explicitly iterate `tree.body` and `ClassDef.body`; relying on `ast.walk()` will overcount nested functions and distort coverage metrics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
