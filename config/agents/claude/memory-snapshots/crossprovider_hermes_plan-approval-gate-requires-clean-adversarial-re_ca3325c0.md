---
name: crossprovider hermes plan-approval-gate-requires-clean-adversarial-re
description: Plan approval gate requires clean adversarial review or explicit user override
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, adversarial-review, plan-governance]
---

Do not auto-approve after plan revisions; surface review findings (APPROVE/MINOR/MAJOR) to user for explicit gate decision. Governance/schema/TDD reviews often uncover independent blockers. Approval remains blocked until clean review or explicit user acceptance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
