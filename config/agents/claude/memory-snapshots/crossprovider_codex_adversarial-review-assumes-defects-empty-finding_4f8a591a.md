---
name: crossprovider codex adversarial-review-assumes-defects-empty-finding
description: Adversarial review assumes defects; empty finding list is failure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [review, quality-gate, adversarial]
---

Adversarial reviews must assume defects until proven otherwise. Every critical claim (plan assertions, implementation details) must be actively verified against code. If no defects are found, list the checks performed instead of claiming clean-pass; an empty review without a methodology record is grounds for rejection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
