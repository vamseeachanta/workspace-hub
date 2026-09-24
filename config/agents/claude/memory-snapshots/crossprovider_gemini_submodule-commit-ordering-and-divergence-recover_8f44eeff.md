---
name: crossprovider gemini submodule-commit-ordering-and-divergence-recover
description: Submodule commit ordering and divergence recovery
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-submodules, multi-repo]
---

Commit changes inside submodule first, then `git add <submodule>` at parent level. For diverged submodules, use `git pull --no-rebase` (merge strategy per CLAUDE.md, never rebase). Detached HEAD in submodules is normal; fix with `git checkout main && git pull --no-rebase`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
