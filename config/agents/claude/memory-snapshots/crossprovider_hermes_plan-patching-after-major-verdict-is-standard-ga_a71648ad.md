---
name: crossprovider hermes plan-patching-after-major-verdict-is-standard-ga
description: Plan patching after MAJOR verdict is standard gate workflow
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, plan-review, gates]
---

Across multiple issues (#88, #2720), the pattern is: create plan → run adversarial review → receive MAJOR → patch plan locally → re-run review → move to status:plan-review. Patching before user approval is expected; re-review ensures patches resolved findings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
