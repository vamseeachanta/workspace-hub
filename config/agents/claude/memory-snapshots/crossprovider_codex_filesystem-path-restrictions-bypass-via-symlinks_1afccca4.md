---
name: crossprovider codex filesystem-path-restrictions-bypass-via-symlinks
description: Filesystem path restrictions bypass via symlinks and relative traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security, filesystem, path-safety]
---

Even when paths are constrained to a directory (e.g., must be under `artifacts/`), symlinks and relative path components (`../`) can escape. Solution: use full path resolution (`repo_path(...).resolve()`) and check the resolved path is still within the intended boundary, not the input path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
