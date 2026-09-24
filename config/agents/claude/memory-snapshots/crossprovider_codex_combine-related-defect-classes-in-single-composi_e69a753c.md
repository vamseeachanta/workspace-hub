---
name: crossprovider codex combine-related-defect-classes-in-single-composi
description: Combine related defect classes in single composite red tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [TDD-pattern, regression-testing, validator-composition]
---

When multiple validators catch related defects (plan_path mismatch, empty path, status drift), combine them in one regression test to verify all checks run together and catch interaction bugs. Individual tests that pass separately can mask cascading failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
