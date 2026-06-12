---
name: crossprovider hermes evidence-gated-execution-progression-through-sta
description: Evidence-gated execution progression through staged gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution, gates, evidence-requirements, tdd]
---

Structure code execution through explicit gates: TDD failing-proof → minimal fix loop → targeted validation (fast checks → requirement proof → behavior confirmation → regression bounds) → adversarial review (PASS/MINOR/MAJOR classifications) → commit/push gate (scope/hygiene/revalidation) → unified closeout with evidence bundle (result/acceptance/validation/review/git proof/residual risk).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
