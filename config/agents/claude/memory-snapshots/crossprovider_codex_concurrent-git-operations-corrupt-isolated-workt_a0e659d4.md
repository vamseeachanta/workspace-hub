---
name: crossprovider codex concurrent-git-operations-corrupt-isolated-workt
description: Concurrent git operations corrupt isolated worktree metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-worktrees, concurrency-hazard, isolation]
---

Long-running sessions in separate worktrees can orphan metadata (missing `.git`, `wikis`, `scripts` directories) when concurrent processes interfere. Status probes on broken worktree paths hang. Mitigation: use the canonical checkout for long-lived work; reserve worktree isolation only for short-lived transforms with explicit cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
