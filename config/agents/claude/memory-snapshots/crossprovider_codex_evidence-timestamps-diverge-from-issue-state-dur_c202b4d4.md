---
name: crossprovider codex evidence-timestamps-diverge-from-issue-state-dur
description: Evidence timestamps diverge from issue state during review windows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [timing, evidence, issue-transitions]
---

When review artifacts are created at time T1 and the issue is reviewed at time T2, the evidence timestamps in the plan no longer match current issue state (no comments yet, no status labels yet). Plans must account for this time window and specify what evidence must be pushed and what comment must be posted before the status transition, not after. Stale timestamps in plan vs. fresh issue state is a common blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
