---
name: crossprovider codex scope-rewrite-is-a-recurring-plan-defect-child-i
description: Scope rewrite is a recurring plan defect: child issues don't cover parent deliverables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-defects, scope-drift, child-issue-coverage]
---

Issue #2452 plan example: parent issue required 'fix highest-leverage clusters first' and 'restore Lint job to green on main,' but plan redefined success as 'decomposition only' with green requirement pushed to child issues. Child issues (#2467, #2468) then scoped only to subsets (single file, safe-rule families) excluding known failures (E722, F841, F541). Adversarial reviews should flag when Deliverable/Acceptance Criteria diverge from parent issue's stated outcome.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
