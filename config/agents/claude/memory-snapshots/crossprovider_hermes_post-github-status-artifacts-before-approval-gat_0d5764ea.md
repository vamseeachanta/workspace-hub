---
name: crossprovider hermes post-github-status-artifacts-before-approval-gat
description: Post GitHub status + artifacts BEFORE approval gate, then stop
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, gate-discipline, planning-first]
---

For planning-first workflow: post concise status comment + plan artifact link on GitHub issue, confirm labels remain `status:needs-plan` or `status:plan-review` (no approval label applied), then STOP. Do not request approval in the same comment; separate gate. User will explicitly say "approved" to move forward.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
