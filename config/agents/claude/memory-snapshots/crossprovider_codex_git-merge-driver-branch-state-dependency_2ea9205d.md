---
name: crossprovider codex git-merge-driver-branch-state-dependency
description: Git merge-driver branch-state dependency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, merge-driver, gitattributes, ingest]
---

Merge drivers (e.g., `merge=union` in .gitattributes) are activated based on the .gitattributes present in the current branch state BEFORE the merge runs, not from what the merge introduces. Stale branches that predate .gitattributes need to explicitly adopt it from origin/main before merging to activate the driver, otherwise append-only files will conflict instead of auto-resolving.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
