---
name: crossprovider codex parallel-work-isolation-is-mandatory-for-quality
description: Parallel work isolation is mandatory for quality
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [parallel-work, isolation, git-workflow, quality]
---

When a collision is detected mid-work, immediately create a clean worktree and isolate from the contaminated path. This prevents downstream defects and preserves audit trails; don't resolve/merge on the fly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
