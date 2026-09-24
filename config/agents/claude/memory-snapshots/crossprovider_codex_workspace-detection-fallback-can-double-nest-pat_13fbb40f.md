---
name: crossprovider codex workspace-detection-fallback-can-double-nest-pat
description: Workspace detection fallback can double-nest paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, path-handling, architecture]
---

If fallback workspace detection returns a subdirectory (e.g., `$HOME/.claude` instead of workspace root), downstream path building appends `.claude/` again, yielding invalid paths like `$HOME/.claude/.claude/...`. Ensure fallback returns only valid workspace roots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
