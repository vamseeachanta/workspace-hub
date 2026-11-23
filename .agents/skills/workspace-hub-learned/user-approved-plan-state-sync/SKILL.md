---
name: user-approved-plan-state-sync
description: Reconcile GitHub and local repo state when a plan has been user-approved, preserving historical owner approval records without making them implementation prerequisites.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [github, planning, governance, approval-state, drift-cleanup]
---

# Optional Owner Approval History Sync

Use only when the owner explicitly requests recording or correcting approval
history. Implementation follows the originating task or standing authority after
planning, TDD and adversarial review, without separate plan approval or markers.

1. Read live issue, plan and review state; inspect implementation history first.
2. Verify the actual owner message and its scope. Labels and markers alone do not
   authenticate authority; do not infer approval from a queue or handoff.
3. Preserve historical labels/markers. Correct records only within the owner's
   explicit request; never self-label approval or create approval to satisfy a hook.
4. Keep private provenance in its authorized location; public comments must be safe.
5. Stage only explicitly requested record changes, verify them and post a traceable
   summary within messaging/publication authority.
6. For implementation, verify task scope, reviewed plan, domain decisions, claims
   and tests independently. A missing history marker is not a blocker.

Retain consequential-action controls, completeness and cleanup checks. Explicit
planning-only requests and holds remain binding.
