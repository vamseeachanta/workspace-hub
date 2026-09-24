---
name: crossprovider codex dependency-sequencing-needs-state-validation-red
description: Dependency sequencing needs state validation RED tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, sequencing, tdd, multi-issue]
---

Plans that state 'depends on issue #N' are loose coupling. Add RED tests that verify completion markers of prior issues exist (e.g., `.planning/plan-approved/(N-1).md`). This catches the case where an artifact exists but prior approval/implementation is incomplete. Allows implementer to stop early with a clear failure message.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
