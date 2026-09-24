---
name: crossprovider codex hardcoded-validator-allowlists-require-code-chan
description: Hardcoded validator allowlists require code changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, validators, coupling]
---

Systems with curated validator lists (manifest checkers, query-surface registries) do not accept new entities from file additions alone. Adding a new domain/source requires updating validator source code to include it in the allowlist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
