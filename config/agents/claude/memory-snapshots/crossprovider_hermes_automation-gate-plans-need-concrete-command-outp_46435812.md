---
name: crossprovider hermes automation-gate-plans-need-concrete-command-outp
description: Automation gate plans need concrete command/output/integration contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, automation, integration]
---

Plans that promise 'integrate with weekly review' without specifying CLI command, output paths, and workflow invocation point are underspecified for implementation. Require explicit: where in workflow it runs, exact command, output artifact paths, how downstream consumes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
