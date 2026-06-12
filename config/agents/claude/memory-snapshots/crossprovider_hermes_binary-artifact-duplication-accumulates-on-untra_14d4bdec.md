---
name: crossprovider hermes binary-artifact-duplication-accumulates-on-untra
description: Binary artifact duplication accumulates on untracked file renames
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, artifact-bloat, untracked-files]
---

When untracked PNG/PDF exports (1+ MB each) are renamed to preserve previous versions, renaming creates silently duplicated assets when later committed. No .gitignore gate or cleanup step prevents accumulation. Explicitly clean up or add to .gitignore before renaming operations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
