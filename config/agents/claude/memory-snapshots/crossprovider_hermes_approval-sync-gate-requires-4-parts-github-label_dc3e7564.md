---
name: crossprovider hermes approval-sync-gate-requires-4-parts-github-label
description: Approval-sync gate requires 4 parts: GitHub label + local marker + comment + push
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-labels, git-markers]
---

Successful approval-sync workflow (session 16) requires all four: (1) `status:plan-approved` label on GitHub issue, (2) `.planning/plan-approved/<N>.md` local marker file, (3) sync comment with commit link, (4) commit + push to main. Skipping any part leaves approval state ambiguous for downstream execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
