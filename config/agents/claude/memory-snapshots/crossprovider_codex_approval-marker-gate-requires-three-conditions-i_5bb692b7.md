---
name: crossprovider codex approval-marker-gate-requires-three-conditions-i
description: Approval marker gate requires three conditions in sync
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [github-gates, approval-compliance, plan-revision]
---

Hard gate to implementation: live GitHub `status:plan-approved` label + revision-bound `.planning/plan-approved/<issue>.md` marker file + matching local plan artifact (not stale draft). When any mismatch detected (live approved but no marker file, or marker bound to commit X while worktree at Y), block implementation and post blocker evidence instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
