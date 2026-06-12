---
name: crossprovider hermes approval-state-lives-in-multiple-places-reconcil
description: Approval state lives in multiple places; reconcile GitHub labels with local proof artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, distributed-state, verification]
---

workspace-hub #2550 was live-labeled `status:plan-approved` but the local `.planning/plan-approved/2550.md` marker was missing and the plan artifact still showed MAJOR findings. This deadlock persisted across multiple sessions. For approval-gated work, verify both the GitHub label AND the local proof artifact before proceeding; either alone is insufficient.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
