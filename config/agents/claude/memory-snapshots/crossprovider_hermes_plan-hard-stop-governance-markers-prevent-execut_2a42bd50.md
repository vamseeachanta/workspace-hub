---
name: crossprovider hermes plan-hard-stop-governance-markers-prevent-execut
description: Plan hard-stop governance markers prevent execution-ready misinterpretation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, planning, github-workflow]
---

Plans marked 'draft' are still interpreted as execution-ready once local review artifacts exist, bypassing approval gates. Add an explicit hard-stop note immediately after the Deliverable or Pseudocode section stating the plan is draft-only and no implementation may begin until adversarial review is complete, posted to GitHub, and user applies status:plan-approved. Location matters—notes elsewhere are overlooked.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
