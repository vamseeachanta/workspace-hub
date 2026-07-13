---
name: crossprovider codex repository-first-workflow-commit-checkpoints-use
description: Repository-first workflow: commit checkpoints, use /tmp only transiently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [workflow, git-practices, artifact-management]
---

Keep durable artifacts in the canonical repo from the start on a dedicated branch/worktree. Clean task-owned residue continuously, commit each verified checkpoint with scoped pathspec commits. Use /tmp only for transient handoffs between phases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
