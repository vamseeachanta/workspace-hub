---
name: crossprovider codex workspace-divergence-with-auto-sync-state
description: Workspace divergence with auto-sync state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, diverged-repos, auto-sync, shared-checkouts]
---

When a repo has auto-generated state (reports, memory, provider configs) that diverges from incoming source changes, they should not be committed together. Stale generated reports committed before pulling source defeat their purpose; instead: clean/stash generated first, pull source, then regenerate reports to reflect new code state. Pathspec commits (`git commit -- <paths>`) are essential to avoid sweeping unrelated dirty work in shared checkouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
