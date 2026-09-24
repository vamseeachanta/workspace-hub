---
name: crossprovider codex pytest-collection-hangs-when-extra-dependency-gr
description: Pytest collection hangs when extra dependency groups not installed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, dependencies, testing-patterns]
---

When tests require optional dependency groups (e.g., `[knowledge-semantic]`), pytest collection can hang if dependencies are not resolved. Run narrow test files individually to isolate TDD signal and confirm dependency install is needed before fixing code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
