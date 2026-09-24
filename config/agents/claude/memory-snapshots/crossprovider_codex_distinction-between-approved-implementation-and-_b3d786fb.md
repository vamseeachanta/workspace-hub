---
name: crossprovider codex distinction-between-approved-implementation-and-
description: Distinction between approved-implementation and plan-review-only is load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-workflow, status-labels, gates]
---

An issue can be `status:plan-review` (ready for review but not approved to start) vs `status:plan-approved` (approved to start implementation) vs `status:blocked` (cannot proceed without external decision). Do not assume a plan in review is ready to implement; check the live labels. For parent epics, the parent's approval status may differ from child implementation readiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
