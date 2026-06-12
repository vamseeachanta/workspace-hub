---
name: crossprovider hermes dirty-workspace-preservation-as-standing-constra
description: Dirty workspace preservation as standing constraint
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace, dirty-state, constraint, commit-scoping, preservation]
---

The `/mnt/local-analysis/workspace-hub` directory retains persistent unrelated modified/untracked files across sessions. Agents must preserve this dirty state without cleaning, staging, or committing unrelated paths. This standing constraint affects commit scoping (use pathspec-mode commits to isolate target files), worktree decisions (isolation vs shared dirty state), and cleanup logic (must not touch unrelated files).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
