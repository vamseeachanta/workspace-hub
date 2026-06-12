---
name: crossprovider hermes readiness-logic-fails-open-when-git-metadata-mis
description: Readiness logic fails open when .git metadata missing; should fail closed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, git-state, dispatch-safety, defect]
---

_collect_git_sync_state() returns (False, 0, 0, []) when .git is absent, signaling clean state. For dispatch readiness, missing .git or unavailable git state should mark dirty=True and append failures, not warnings. Current logic sets status=warn/dispatchable=True when only warnings exist, risking dispatch of unsynced hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
