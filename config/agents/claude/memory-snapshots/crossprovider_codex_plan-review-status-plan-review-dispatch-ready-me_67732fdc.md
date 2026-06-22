---
name: crossprovider codex plan-review-status-plan-review-dispatch-ready-me
description: Plan review status: plan-review + dispatch-ready means planning-only, not executable
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [workflow, lifecycle]
---

A GitHub issue with both `status:plan-review` and `dispatch:ready` is still planning-only until user explicitly moves it to `status:plan-approved`. Dispatcher logic will not execute `plan-review` work; approval is a separate authorization step from triage readiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
