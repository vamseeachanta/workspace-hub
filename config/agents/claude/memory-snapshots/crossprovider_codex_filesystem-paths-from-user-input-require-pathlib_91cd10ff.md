---
name: crossprovider codex filesystem-paths-from-user-input-require-pathlib
description: Filesystem paths from user input require pathlib validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, path-traversal, filesystem]
---

Session 21 identified path traversal risk in RAO registry where `hull_id` and `solver` were used directly in paths with no sanitization. User input must validate via `pathlib.Path.relative_to()`, reject absolute paths and `..` segments, and document trust boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
