---
name: crossprovider hermes falsifiable-acceptance-criteria-never-use-or-equ
description: Falsifiable acceptance criteria: never use 'or equivalent' or undefined thresholds
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [acceptance-criteria, testability, defect-class]
---

Plans with tests like 'N lines added' (N undefined), 'or equivalent' exemptions, or branch-diff checks are unverifiable. Correctness gates require explicit binary-outcome conditions: 'file exists AND contains X' not 'similar structure or thereabouts'. Defect class: phantom test gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
