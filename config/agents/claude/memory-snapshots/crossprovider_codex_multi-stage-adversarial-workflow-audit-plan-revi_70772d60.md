---
name: crossprovider codex multi-stage-adversarial-workflow-audit-plan-revi
description: Multi-stage adversarial workflow: audit → plan-review → TDD → code-review → verify
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-pattern, adversarial-review, tdd, high-stakes, scheduler]
---

Complex high-stakes code (scheduler mutations, enforcement governance) benefits from alternating read-only audits, adversarial plan reviews to surface blockers, TDD implementation phases with RED→GREEN rigor, adversarial code reviews with static-only targeted checks, and final verification gates. Each stage catches defect classes the prior stage missed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
