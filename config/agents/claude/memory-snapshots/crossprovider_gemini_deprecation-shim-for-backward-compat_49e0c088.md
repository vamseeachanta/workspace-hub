---
name: crossprovider gemini deprecation-shim-for-backward-compat
description: Deprecation shim for backward compat
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, backward-compat, pattern]
---

When refactoring a module into multiple files, leave a ~15-line shim with `warnings.warn()` + re-exports. Breaks callers only if they upgrade; most old imports still work. Prefer to self-labeling approach.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
