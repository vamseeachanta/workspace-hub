---
name: crossprovider hermes readiness-logic-fail-open-on-missing-git
description: Readiness logic fail-open on missing .git
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-safety, readiness, git-state, workspace-hub-2720]
---

When workspace_root has no `.git` directory, `_collect_git_sync_state()` returns `(False, 0, 0, [])`, treating the directory as clean/synced. For dispatch readiness, missing `.git` should fail closed, not report pass/warn status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
