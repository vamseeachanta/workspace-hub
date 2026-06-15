---
name: crossprovider codex worktree-path-dependency-sync-workaround-for-mon
description: Worktree path-dependency sync workaround for monorepos
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [worktree, uv-python, monorepo, dependency-resolution]
---

Fresh worktrees created from origin/main in monorepos with path dependencies (e.g., `./assetutilities`) fail during `uv run` dependency resolution. Set `UV_NO_SYNC=1` before running focused tests to work around missing sibling paths in isolated worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
