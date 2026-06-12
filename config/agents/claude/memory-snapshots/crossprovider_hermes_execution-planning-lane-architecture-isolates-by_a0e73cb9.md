---
name: crossprovider hermes execution-planning-lane-architecture-isolates-by
description: Execution + planning lane architecture isolates by repo + serial
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git-contention, worktree-strategy]
---

Parallel execution lanes require per-repo worktrees (assethold, worldenergydata, workspace-hub separate). Serial planning lane requires single worktree for shared-doc edits (#2441/#2443/#2444 in workspace-hub). Failure to serialize planning commits cross-editing README.md triggers git lock contention.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
