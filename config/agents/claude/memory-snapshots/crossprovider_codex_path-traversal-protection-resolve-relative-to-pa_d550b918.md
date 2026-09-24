---
name: crossprovider codex path-traversal-protection-resolve-relative-to-pa
description: Path traversal protection: resolve() + relative_to() pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, path-traversal, pathlib]
---

Safe workspace reference resolution: `resolve()` the candidate path, then call `relative_to(workspace_root.resolve())` and catch `ValueError` if it escapes. Returns `None` for out-of-bounds paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
