---
name: crossprovider codex fresh-isolated-worktrees-may-lack-local-path-dep
description: Fresh isolated worktrees may lack local path dependencies, blocking full workspace syncs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [worktrees, dependencies, uv, tdd]
---

When checking out origin/main into a new isolated worktree, path dependencies (e.g., ./assetutilities) may not exist. Use UV_NO_SYNC=1 to enable focused test runs without triggering a full workspace sync, allowing P1-scoped work before broadening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
