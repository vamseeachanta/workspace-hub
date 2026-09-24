---
name: crossprovider gemini metapathfinder-redirect-pattern-for-backward-com
description: MetaPathFinder redirect pattern for backward-compatible module reorganization
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python-patterns, refactoring, backward-compat, import-system]
---

When flattening Python package hierarchies (e.g., `src.modules.X` → `src.X`), install a MetaPathFinder on sys.meta_path to intercept old import paths, redirect to new paths, and emit DeprecationWarning. Combine with `__getattr__` on the old namespace package to handle attribute-access imports. This enables large-scale refactoring without breaking existing code and guides callers to migrate at their own pace.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
