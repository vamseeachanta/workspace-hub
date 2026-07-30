---
name: crossprovider codex canonical-workspace-hub-contains-bootstrap-files
description: Canonical workspace-hub contains bootstrap files missing from repo worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [environment, bootstrap]
---

Repository worktrees lack `.claude/lifecycle`, `.claude/memory`, and other bootstrap paths present in workspace-hub. Load instructions from workspace-hub sibling before assuming they exist locally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
