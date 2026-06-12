---
name: crossprovider hermes parallel-hermes-sessions-avoid-git-conflicts-via
description: Parallel Hermes sessions avoid git conflicts via temp issue staging
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-agents, git-safety, github-staging, workflow-pattern]
---

Multiple concurrent Hermes agents on workspace-hub avoid `git commit` races by staging issue-comment bodies to `/tmp` before posting to GitHub, keeping main worktree clean. Verified pattern: probe script writes `/tmp/multimachine-control-surface-status-*.md`, then posts via `gh issue comment` with file path. Preserves parallel-session git safety.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
