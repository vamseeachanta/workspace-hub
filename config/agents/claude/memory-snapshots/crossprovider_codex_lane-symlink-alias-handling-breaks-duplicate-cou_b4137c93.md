---
name: crossprovider codex lane-symlink-alias-handling-breaks-duplicate-cou
description: Lane symlink/alias handling breaks duplicate-count and coverage assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-structure-hazard, llm-wiki, file-system-semantics]
---

Symlinks like `docs/_standards -> O&G-Standards/` cause double-counting in overlap detection or false exclusion if not explicitly handled. Alias traversal policy must be decided and tests must enumerate both sides.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
