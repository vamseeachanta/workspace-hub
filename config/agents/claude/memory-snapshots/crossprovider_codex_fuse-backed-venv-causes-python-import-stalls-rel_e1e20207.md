---
name: crossprovider codex fuse-backed-venv-causes-python-import-stalls-rel
description: FUSE-backed .venv causes Python import stalls; relocate to local ext4
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [performance, fuse, python, tdd]
---

/mnt/local-analysis on fuseblk stalls on small-file traversal of large .venv (372+ packages). Move test-only environments to /tmp/ via UV_PROJECT_ENVIRONMENT=/tmp/venv; keep repo writes in the assigned worktree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
