---
name: crossprovider hermes runtime-probe-evidence-can-overstate
description: Runtime probe evidence can overstate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [evidence, validation, provisioning]
---

Checking indirect evidence ('does parent directory exist?') is weaker than direct probe. Status marked 'present_recorded' from checking `/mnt/local-analysis` existence doesn't confirm target itself provisioned/reachable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
