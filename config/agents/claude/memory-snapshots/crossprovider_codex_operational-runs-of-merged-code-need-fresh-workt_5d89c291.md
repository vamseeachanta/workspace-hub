---
name: crossprovider codex operational-runs-of-merged-code-need-fresh-workt
description: Operational runs of merged code need fresh worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [worktree-isolation, operational-runs, branch-freshness, merged-code-validation]
---

Even when running validation of already-implemented code (e.g., scheduler jobs, refresh operations), create a clean worktree from origin/main. A stale local branch won't reflect the merged code, risking silent failures or inconsistent production output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
