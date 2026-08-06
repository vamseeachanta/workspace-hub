---
name: crossprovider codex silent-auto-sync-commits-during-session-reflog-r
description: Silent auto-sync commits during session; reflog reveals; mixed reset preserves work
metadata:
  type: reference
  source: codex
  bridged: 2026-08-05
  tags: [git, automation, workflow-safety, common-hazard]
---

When explicit 'do not commit' instruction is given but git status becomes unexpectedly clean, check reflog to detect auto-sync commits. Use `git reset --mixed <known-clean-commit>` to safely undo the commit while preserving all working-tree changes. This pattern appeared in three sessions (2026-08-04 GREEN-wave and RED-wave phases).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
