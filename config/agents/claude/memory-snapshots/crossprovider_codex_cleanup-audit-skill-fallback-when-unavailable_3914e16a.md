---
name: crossprovider codex cleanup-audit-skill-fallback-when-unavailable
description: Cleanup audit skill fallback when unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, audit, fallback]
---

The workspace instructions reference `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`, but it is often not present in worktrees. Fallback: run `git status --short` and `git stash list` manually; check for pre-existing `.cleanup-trash/` and `/tmp/` residue; only treat newly modified tracked files as task-generated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
