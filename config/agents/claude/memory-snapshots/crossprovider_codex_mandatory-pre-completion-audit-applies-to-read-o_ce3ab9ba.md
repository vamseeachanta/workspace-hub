---
name: crossprovider codex mandatory-pre-completion-audit-applies-to-read-o
description: Mandatory pre-completion audit applies to read-only subtasks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, audit, governance]
---

Repository cleanup audit gates apply even to read-only audit passes. When the cleanup skill is unavailable at its documented path, perform equivalent checks manually: git status, git diff, worktree residue inspection. This prevents read-only passes from leaving hidden state that blocks later operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
