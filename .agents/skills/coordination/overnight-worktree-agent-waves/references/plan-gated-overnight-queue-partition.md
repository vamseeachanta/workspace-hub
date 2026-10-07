# Archived Skill: `plan-gated-overnight-queue-partition`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-gated-overnight-queue-partition`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-gated-overnight-queue-partition`
Consolidation date: 2026-04-29

---

---
name: plan-gated-overnight-queue-partition
description: Partition a plan-gated GitHub queue before launching overnight work so review-blocked or out-of-scope issues are routed to planning and scope-authorized issues proceed to implementation; merging retains action-specific authority.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [github, overnight, plan-gated, queue-triage, execution]
---

# Reviewed Overnight Queue Partition

Current authority: implementation follows the originating task request or established standing authority after proportionate planning, TDD and adversarial review; no separate plan approval, approval label or local marker is required. Planning-only limits, unresolved domain decisions and action-specific authorization for publication, deployment, access changes, destructive actions and outreach remain binding. Historical approval records stay intact and must not be fabricated or self-labeled.

Use when the user asks for overnight parallel implementation, review or merging.
The request may authorize implementation even when historical approval labels
are absent. Verify actual merge/publication authority separately.

## Required live partition

1. Reviewed scope within task authority: eligible for TDD implementation.
2. Planning-only request or missing plan/review: resource intelligence and review.
3. Blocking review finding or required domain decision: resolve the named blocker.
4. Active claim/worker: coordinate before dispatching another lane.
5. Implementation complete: validate, adversarially review and follow closeout controls.

Refresh live issues, plan/review artifacts, originating task scope, claims and
worktree state before dispatch. Historical labels/markers may inform discovery
but neither grant authority nor block authorized work. Honor explicit holds.
Keep tests, review, security, completeness and cleanup controls. Never infer
merge authorization merely from implementation authority or overnight timing.
