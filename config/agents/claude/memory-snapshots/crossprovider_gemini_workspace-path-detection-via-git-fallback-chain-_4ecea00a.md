---
name: crossprovider gemini workspace-path-detection-via-git-fallback-chain-
description: Workspace path detection via git fallback chain handles submodules
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [path-resolution, submodules, shell-patterns]
---

`${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}` resolves env var → superproject (for nested repos) → toplevel. Robust for hooks across monorepo without hardcoded paths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
