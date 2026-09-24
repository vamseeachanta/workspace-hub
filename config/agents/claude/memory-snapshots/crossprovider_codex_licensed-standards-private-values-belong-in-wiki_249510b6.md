---
name: crossprovider codex licensed-standards-private-values-belong-in-wiki
description: Licensed standards private values belong in wiki, not code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, licensing, architecture, wiki]
---

When implementing licensed standards (e.g., AMJIG drilling guidelines), public identifiers can live in code, but private numeric values must resolve from `LLM_WIKI_PATH` at test/runtime, never hardcoded in fixtures or public code. This separates provenance (wiki) from public schema (code).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
