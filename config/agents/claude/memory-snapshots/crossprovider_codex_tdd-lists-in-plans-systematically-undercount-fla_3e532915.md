---
name: crossprovider codex tdd-lists-in-plans-systematically-undercount-fla
description: TDD lists in plans systematically undercount flag combinations and error paths
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [test-coverage-gaps, plan-review]
---

Plan TDD lists often enumerate happy paths but miss: CLI flag negations (--no-flag), hard-failure exit codes tied to flags, error-case branches (missing files, invalid input), and flag precedence conflicts. Adversarial review should explicitly enumerate all CLI flags and their cross-product coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
