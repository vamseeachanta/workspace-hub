---
name: crossprovider codex workspace-detection-fallback-paths-must-normaliz
description: Workspace detection fallback paths must normalize to root
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [path-resolution, workspace-detection, cross-platform]
---

When resolving workspace location via fallback detection, paths like `$HOME/.claude` must be normalized to the workspace root before downstream code appends subpaths (`/.claude/state/...`), or double-nesting results (`$HOME/.claude/.claude/state/...`). Always return the workspace root, not subdirectories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
