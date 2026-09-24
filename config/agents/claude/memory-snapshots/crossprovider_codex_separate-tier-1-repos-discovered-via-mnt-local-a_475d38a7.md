---
name: crossprovider codex separate-tier-1-repos-discovered-via-mnt-local-a
description: Separate tier-1 repos discovered via /mnt/local-analysis/workspace-hub/<repo>
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [repo-structure, worktree-isolation, multi-repo-discovery]
---

When an approved plan targets paths missing from the current workspace-hub worktree (e.g., tier-1 `digitalmodel/`, `assetutilities/`, `assethold/`), check for standalone repos at `/mnt/local-analysis/workspace-hub/<repo>`. Create isolated worktrees from their `origin/main` to avoid mutating unrelated checked-out branches on those repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
