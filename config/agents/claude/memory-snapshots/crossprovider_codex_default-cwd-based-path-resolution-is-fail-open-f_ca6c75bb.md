---
name: crossprovider codex default-cwd-based-path-resolution-is-fail-open-f
description: Default cwd-based path resolution is fail-open for private data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-safety, default-arguments, private-data, fail-open]
---

When code uses `os.getcwd()` or similar to infer a repo root for private data path enforcement, it fails open if invoked from the wrong directory. Always require explicit `--repo-root` or infer from script location, then verify the path is outside the git worktree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
