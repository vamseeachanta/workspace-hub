---
name: crossprovider codex pre-push-hook-blocks-isolated-worktrees-missing-
description: Pre-push hook blocks isolated worktrees missing sibling tier-1 repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, isolated-worktree, push-bypass]
---

workspace-hub's pre-push hook validates presence of sibling tier-1 repos (`assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `aceengineer-admin`). Isolated worktrees lack these; normal push fails with topology errors. Use `--no-verify` (after validation passes) or `GIT_PRE_PUSH_SKIP=1` env var for audited bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
