---
name: crossprovider gemini submodule-diff-metadata-pollution-indicates-work
description: Submodule diff metadata pollution indicates workspace contamination
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, submodules, workspace]
---

Git diffs of submodule pointer updates sometimes embed context from unrelated submodules (e.g., assethold paths in worldenergydata diffs), signaling overlapping worktrees or dirty state. Validate clean worktree before submodule updates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
