---
name: crossprovider hermes approval-gate-requires-both-github-label-and-loc
description: Approval gate requires both GitHub label and local marker file
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, approval-gate]
---

`.planning/plan-approved/N.md` marker file + GitHub `status:plan-approved` label work together. Neither alone is sufficient. Marker records approval source (e.g., Hermes chat); label gates issue in GitHub. Both enable gating without self-approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
