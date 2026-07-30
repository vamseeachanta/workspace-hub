---
name: crossprovider codex fail-closed-wiki-backed-getters-for-standards-va
description: Fail-closed wiki-backed getters for standards values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, standards, test-driven-development]
---

Pattern: private standards values (e.g., AMJIG limits) are resolved at query time via `LLM_WIKI_PATH` getters, not hardcoded. Tests must prove direct calls fail closed without the wiki path and never commit standard-specific numbers to public fixtures. This decouples public code from licensed data while maintaining fail-closed semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
