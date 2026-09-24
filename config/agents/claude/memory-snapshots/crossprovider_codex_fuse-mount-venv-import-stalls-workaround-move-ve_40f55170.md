---
name: crossprovider codex fuse-mount-venv-import-stalls-workaround-move-ve
description: FUSE mount .venv import stalls—workaround: move .venv to local ext4
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fuse, python, venv, performance]
---

On `/mnt/local-analysis` (fuseblk), Python imports from large `.venv` stall during small-file traversal. Move only `.venv` to local ext4 via `UV_PROJECT_ENVIRONMENT=/tmp/<env>` while keeping project files on FUSE. Eliminates import latency without breaking lock reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
