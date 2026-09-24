---
name: crossprovider codex multi-artifact-state-consistency-is-load-bearing
description: Multi-artifact state consistency is load-bearing for issue transitions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, issue-planning, coordination]
---

When a project coordinates state across issue body, plan file, coordination ledger, and evidence artifacts, stale or inconsistent references block transitions. Reviewers cannot approve status changes if issue-body blockers are stale, review artifacts are timestamped differently than the plan references them, or the coordination ledger disagrees with the plan's gate claims. Must verify state parity across all four surfaces before approving plan-review transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
