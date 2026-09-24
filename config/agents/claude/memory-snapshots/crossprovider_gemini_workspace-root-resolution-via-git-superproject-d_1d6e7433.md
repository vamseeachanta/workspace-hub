---
name: crossprovider gemini workspace-root-resolution-via-git-superproject-d
description: Workspace root resolution via git superproject detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [path-resolution, monorepo, workspace-hub, git]
---

Use `git rev-parse --show-superproject-working-tree` with fallback to `git rev-parse --show-toplevel` to robustly resolve workspace root in both monorepo (superproject) and standalone-repo scenarios. This pattern appears in session hooks and allows scripts to operate correctly regardless of checkout structure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
