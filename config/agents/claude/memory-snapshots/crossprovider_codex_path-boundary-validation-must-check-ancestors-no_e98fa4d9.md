---
name: crossprovider codex path-boundary-validation-must-check-ancestors-no
description: Path boundary validation must check ancestors, not just final symlinks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [security, path-validation, symlinks]
---

Rejecting `is_symlink()` on the final path misses symlink directories in ancestors. A path under a symlinked directory can resolve outside the repo. Proper boundary validation requires resolving to canonical form and verifying the canonical path stays within bounds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
