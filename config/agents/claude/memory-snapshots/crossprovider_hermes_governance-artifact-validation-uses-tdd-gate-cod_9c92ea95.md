---
name: crossprovider hermes governance-artifact-validation-uses-tdd-gate-cod
description: Governance artifact validation uses TDD gate + Codex review before commit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, validation-gates, tdd-pattern]
---

Pattern: implement artifact → add unit tests + deterministic validator script → run validator as gate → adversarial Codex review → commit/push only if passing → post evidence comments to blocked parent issues → close. Validators prevent invalid commits; evidence comments re-gate blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
