---
name: crossprovider hermes provider-capacity-fix-is-approved-work-queue-not
description: Provider capacity fix is approved work queue, not more AI spend
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-utilization, work-queuing, dispatch-gates]
---

Core issue: 50% AI credit waste. Fix is NOT deploying agents more aggressively. Fix IS maintaining a ready queue of GitHub-issue-backed, plan-approved, bounded work so unused provider capacity has somewhere safe to dispatch. Telemetry refreshes every 4–6 hours; decision rule: if low usage and approved work exists, dispatch; if low usage and no approved work, plan/review instead of implement.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
