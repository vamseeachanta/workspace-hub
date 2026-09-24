---
name: crossprovider codex filesystem-error-handling-must-wrap-per-child-op
description: Filesystem error handling must wrap per-child operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem, error-handling, robustness]
---

os.OSError handlers in directory traversal must cover individual child stat/is_file/is_dir calls, not just iterdir(). Without this, permission errors, broken symlinks, TOCTOU races, and inaccessible files abort the entire inventory instead of recording errors and continuing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
