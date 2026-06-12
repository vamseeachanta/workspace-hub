---
name: crossprovider hermes worktree-isolation-for-dirty-workspaces-avoids-s
description: Worktree isolation for dirty workspaces avoids sweep contamination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, worktree, contamination-prevention]
---

When main branch accumulates many unrelated modified/untracked files (e.g., 79+ paths), use isolated git worktrees for focused commits. Avoids sweep-contamination pattern where retry-loop or broad `git add -A` accidentally stages unrelated changes. Worktree provides clean index isolation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
