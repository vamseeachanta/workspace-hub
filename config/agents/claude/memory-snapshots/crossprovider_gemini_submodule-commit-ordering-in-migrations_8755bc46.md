---
name: crossprovider gemini submodule-commit-ordering-in-migrations
description: Submodule commit ordering in migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [submodule-ops, git-migrations, commit-ordering]
---

When migrating files that touch submodules, commit changes inside the submodule first with its own message, then update the parent repo pointer in a separate commit. This prevents orphaning the submodule revision state and ensures parent-child coherence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
