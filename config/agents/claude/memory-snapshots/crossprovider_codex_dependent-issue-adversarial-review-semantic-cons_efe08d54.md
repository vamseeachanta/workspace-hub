---
name: crossprovider codex dependent-issue-adversarial-review-semantic-cons
description: Dependent-issue adversarial review: semantic consumption, not presence-check
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [adversarial-review, dependency-validation]
---

When issue A depends on issue B's output, adversarial review must enforce actual semantic consumption: enums enforced, output signals flowing (not collapsed), thresholds real, control flags visible in outputs. Presence-only validators (empty fallbacks, no-op checks) create gaps that fail adversarial gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
