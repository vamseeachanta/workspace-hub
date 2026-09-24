---
name: crossprovider codex dead-code-deletion-requires-more-than-symbol-gre
description: Dead-code deletion requires more than symbol grep for published packages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, package-safety, api-stability]
---

Grep-only deletion analysis misses: importlib/getattr hooks, __all__ public exports, pickle module references, dynamic string loading, external consumers. For published packages, __all__ entries signal explicit public API; deletion requires deprecation shims and full-repo searches including tests, docs, configs, and CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
