---
name: crossprovider codex platform-scoped-verification-scripts-assume-sing
description: Platform-scoped verification scripts assume single repo layout and break in isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [script-portability, worktrees, path-assumptions]
---

Scripts like legal-scan that are workspace-scoped (e.g., resolving --repo=digitalmodel to a workspace-hub child path) fail when called from isolated worktrees where that path doesn't exist. Tool paths must be configurable or relative to the worktree root, not hardcoded to a parent layout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
