---
name: crossprovider codex commit-shas-are-the-only-reliable-ref-during-con
description: Commit SHAs are the only reliable ref during concurrent PR rebases
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [git, code-review, parallel-work, hazard]
---

When multiple code-review sessions run on the same PR, worktrees drift to different commits as the PR is force-pushed. Pinning all file reads, diffs, and reproductions to explicit commit SHAs (not branch names or HEAD) prevents reviewing stale state. This matters because interactive rebases mid-review can leave the worktree at an old commit while the PR has advanced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
