---
name: crossprovider hermes plan-triggered-ci-validator-circular-dependency-
description: Plan-triggered CI validator circular dependency when exemption undefined
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-design, scheduler-validation, exemption-schema]
---

If a new CI validation rule would block existing scheduled jobs (e.g., `gsd-researcher-nightly.sh`), the plan must define either a migration issue reference or an exemption schema in the validator. Otherwise the CI validator itself fails to run because the existing job fails the new rule—a circular blocker.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
