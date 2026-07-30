---
name: crossprovider codex mutable-dependency-pins-like-main-bypass-frozen-
description: Mutable dependency pins like @main bypass frozen resolution silently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [CI, dependencies, tooling]
---

Quality gates using @main or main-branch pins defeat the intended locked/frozen behavior. Traces show domain gates resolving different commits than pinned tests. Must use explicit immutable commit hashes and --locked/--frozen flags; test the parsed command.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
