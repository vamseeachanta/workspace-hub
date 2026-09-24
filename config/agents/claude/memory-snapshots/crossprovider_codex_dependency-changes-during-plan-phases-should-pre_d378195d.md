---
name: crossprovider codex dependency-changes-during-plan-phases-should-pre
description: Dependency changes during plan phases should preserve implementation-ready state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependency-changes, scope-control, approval-gates]
---

When changing an issue's dependencies during planning (e.g., #69 from [68] to [65]), explicitly document whether the issue's `implementation_ready` and approval status change. Allowing implicit approval during dependency fixes is a scope-creep vector.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
