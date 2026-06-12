---
name: crossprovider hermes stash-export-and-drop-pattern-preserves-record-w
description: Stash export-and-drop pattern preserves record while cleaning repo state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-cleanup, stash-management, repository-hygiene, workspace-hub]
---

For stale or obsolete stashes (e.g., absorbed into HEAD or runtime artifacts), export patch/stat/commit metadata off-repo before dropping refs. Prevents stash list pollution, accidental replay, and maintains forensic record. Useful before branch cleanup or parallel-work handoff.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
