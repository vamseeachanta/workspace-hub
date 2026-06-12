---
name: crossprovider hermes plan-patches-require-exact-tdd-proof-not-handwav
description: Plan patches require exact TDD proof, not handwaving
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, plan-review, approval-gate]
---

When responding to adversarial findings, add failing tests first (TDD), then plan implementation. Reviewers reject patches without evidence that tests actually fail. Staged/unimplemented work on a plan weakens approval credibility.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
