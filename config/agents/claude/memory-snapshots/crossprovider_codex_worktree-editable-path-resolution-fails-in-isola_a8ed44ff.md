---
name: crossprovider codex worktree-editable-path-resolution-fails-in-isola
description: Worktree editable-path resolution fails in isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-tooling, worktree-isolation, uv]
---

`uv` resolves relative editables (e.g., `../assetutilities`) as worktree-local paths when invoked inside an isolated worktree, not repo-root paths. Workaround: run with canonical checkout's environment and isolated worktree's PYTHONPATH.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
