---
name: crossprovider hermes lane-completion-state-drifts-from-live-github-la
description: Lane-completion state drifts from live GitHub labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [consistency-hazard, approval-workflow]
---

After a lane completes, GitHub labels/comments may be mutated by other agents/users, creating mismatch with local `.planning/plan-approved/{issue-ids}.md` markers. Verify live GitHub state when assessing promotion-readiness; expect stale local records.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
