---
name: crossprovider hermes cross-provider-consensus-major-blocks-approval-g
description: Cross-provider consensus MAJOR blocks approval gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, multi-provider-review, gates]
---

When Claude+Codex+Gemini all return MAJOR from adversarial review, the issue must NOT transition to status:plan-review or plan-approved. Plan must be revised to address concrete blockers, then re-reviewed. Gate remains at status:needs-plan until reviewers return MINOR or PASS.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
