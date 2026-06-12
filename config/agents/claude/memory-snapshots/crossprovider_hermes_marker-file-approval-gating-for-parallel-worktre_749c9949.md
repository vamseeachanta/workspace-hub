---
name: crossprovider hermes marker-file-approval-gating-for-parallel-worktre
description: Marker-file approval gating for parallel worktree implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gate, parallel-work, worktree-isolation, tdd-workflow, git-coordination]
---

For parallel agent TDD work, use `.planning/plan-approved/<issue>.md` marker files to signal approval state across isolated worktree sessions. Pattern: approve in main checkout, create marker file, commit with plan artifacts, push to origin. Parallel agents check for marker before starting TDD implementation. Avoids git-level blocking and race conditions while preserving a clear approval handoff trail committed to history.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
