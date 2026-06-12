---
name: crossprovider codex path-traversal-defense-resolve-relative-to-valid
description: Path traversal defense: resolve() + relative_to() validates workspace boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, path-handling, input-validation]
---

For user-controlled file paths in script arguments, validate they stay within workspace using `(workspace / candidate).resolve().relative_to(workspace)` wrapped in try/catch ValueError. Catches `../../etc/passwd` and symlink escapes via canonical path comparison; used in generate-final-review.py for plan_draft_ref/plan_final_ref validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
