---
name: crossprovider codex duplicate-error-class-names-in-separate-modules-
description: Duplicate error class names in separate modules break routing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, error-handling]
---

When two modules define the same error class (e.g., `exceptions.py` and `errors.py` both have `ProviderError`), a router selecting by module name can enter a path with the wrong class hierarchy, causing `AttributeError` on expected factory methods like `.unavailable()`. Use a single canonical error module or qualified names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
