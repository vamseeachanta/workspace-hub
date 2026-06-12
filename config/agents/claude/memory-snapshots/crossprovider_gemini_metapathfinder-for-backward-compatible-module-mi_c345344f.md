---
name: crossprovider gemini metapathfinder-for-backward-compatible-module-mi
description: MetaPathFinder for backward-compatible module migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, refactoring, backward-compatibility]
---

Large module structure refactors (e.g., worldenergydata moving 17 modules from `modules/X/` to `X/`) can preserve backward compatibility via Python's import system. Pattern: define MetaPathFinder to intercept old paths, redirect to new, and emit DeprecationWarning. Handle both `import old.path` (finder) and `from old import name` (__getattr__) separately. Re-entrancy guards prevent loops.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
