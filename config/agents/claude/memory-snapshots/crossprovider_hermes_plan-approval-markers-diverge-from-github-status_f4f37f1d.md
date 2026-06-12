---
name: crossprovider hermes plan-approval-markers-diverge-from-github-status
description: Plan-approval markers diverge from GitHub status labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-sync, local-state]
---

Local `.planning/plan-approved/` markers can fall out of sync with GitHub issue status labels. When reconciling approval state, trust the latest-status-precedence: local markers + handoff logs override stale GitHub issue labels. Observed in session 20260413_061204_c51679 where 5+ issues had approval markers but README still showed status:plan-review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
