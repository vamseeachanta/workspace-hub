---
name: crossprovider codex repository-first-commit-as-we-go-workflow
description: Repository-first, commit-as-we-go workflow
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-governance, repository-practice, durable-artifacts, git-discipline]
---

All durable work occurs in canonical repositories on branches/worktrees, not in `/tmp` transient artifacts. Commit each verified checkpoint with scoped pathspec commits (not broad git add). Clean task-owned residue continuously without touching unrelated changes. This approach preserves audit trail, enables concurrent work, and eliminates post-session cleanup debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
