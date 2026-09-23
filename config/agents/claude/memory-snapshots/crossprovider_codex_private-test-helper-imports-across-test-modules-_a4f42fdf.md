---
name: crossprovider codex private-test-helper-imports-across-test-modules-
description: Private test-helper imports across test modules create silent refactor brittleness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [test-architecture, coupling, modularity]
---

Tight coupling to `_builder`, `_git`, `_generate` helpers from other test modules means unrelated refactoring can break coverage without changing product behavior. Extract shared test-support helpers to a dedicated module with a stable boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
