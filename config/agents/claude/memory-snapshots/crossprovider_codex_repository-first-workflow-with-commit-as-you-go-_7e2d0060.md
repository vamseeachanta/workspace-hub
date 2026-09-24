---
name: crossprovider codex repository-first-workflow-with-commit-as-you-go-
description: Repository-first workflow with commit-as-you-go for multi-task work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, repo-hygiene, multi-task]
---

For complex, multi-checkpoint tasks, keep durable artifacts in the canonical repo on a dedicated branch/worktree. Commit scoped pathspec after each verified checkpoint, clean residue continuously, and avoid accumulating work in `/tmp`. This prevents orphan state, lock files, and task-related residue from persisting across sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
