---
name: crossprovider codex lazy-package-exports-via-getattr-prevent-circula
description: Lazy package exports via __getattr__ prevent circular imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [imports, package-structure, world-energy-data-spain]
---

The worldenergydata-spain package uses __getattr__ for lazy exports (loader, live, future density modules) instead of eager imports in __init__.py. This pattern avoids circular dependencies between densely-connected modules and allows scheduler/adapter to import loaders without triggering unnecessary submodule loads. Use for any new Spain production module exports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
