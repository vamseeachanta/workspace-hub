---
name: crossprovider hermes worktree-path-segregation-needed-for-multi-issue
description: Worktree path segregation needed for multi-issue parallel work without git-lock races
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-patterns, git-safety, parallel-execution]
---

Issue-specific worktrees (e.g. `/agent-worktrees/workspace-hub-issue-2766-*`) isolate branches + paths. Serialized commits from main session on specific paths avoid sweep-contamination where retry loops drain unrelated stashes or parallel checkouts revert working dirs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
