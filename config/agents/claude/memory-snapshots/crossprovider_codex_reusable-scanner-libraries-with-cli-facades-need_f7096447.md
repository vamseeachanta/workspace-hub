---
name: crossprovider codex reusable-scanner-libraries-with-cli-facades-need
description: Reusable scanner libraries with CLI facades need explicit import structure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [module-design, api-design, import-patterns]
---

Splitting a scanner into reusable library + CLI wrapper creates import fragility if the library uses bare sibling imports. The wrapper can inject sys.path, but direct imports fail with ModuleNotFoundError. Use explicit package structure (`__init__.py`, relative imports) instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
