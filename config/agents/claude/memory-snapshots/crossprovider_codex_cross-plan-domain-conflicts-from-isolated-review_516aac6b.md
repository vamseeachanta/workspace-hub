---
name: crossprovider codex cross-plan-domain-conflicts-from-isolated-review
description: Cross-plan domain conflicts from isolated review: format policy vs. input acceptance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-plan-conflicts, format-handling, adversarial-review]
---

When one plan requires format X to fail closed (#606) and another adds X to dry-run acceptance (#607), isolated review misses the incompatibility. Tests pass but users hit contradictory behavior. Adversarial review must check related approved plans for domain conflicts in input acceptance, status rules, and format handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
