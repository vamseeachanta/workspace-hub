---
name: crossprovider codex oserror-handling-too-narrow-leaves-filesystem-er
description: OSError handling too narrow leaves filesystem errors unhandled
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, robustness]
---

Wrapping only `iterdir()` in OSError handlers leaves `is_dir()`, `stat()`, `open()`, and per-child hashing/classification unprotected (#2767 #2389 pattern). Phase A inventory must wrap per-child operations and file stat/hash collection in OSError handlers that record InventoryError and continue, preventing abort on inaccessible paths, broken mounts, or special files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
