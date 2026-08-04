---
name: crossprovider codex cleanup-scripts-with-unconditional-exit-mask-par
description: Cleanup scripts with unconditional exit mask partial deletion failures
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [scripting, error-handling, automation, safety]
---

A pattern like `rm -rf dir && exit 0` succeeds unconditionally even if deletion fails partway (directory not empty, permissions, active refs). The harness logs `=== OK ===` while leaving orphaned content behind. Use `|| exit 1` or post-delete verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
