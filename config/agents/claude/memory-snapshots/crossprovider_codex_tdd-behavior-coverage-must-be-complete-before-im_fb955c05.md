---
name: crossprovider codex tdd-behavior-coverage-must-be-complete-before-im
description: TDD behavior coverage must be complete before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, testing, completeness]
---

Tests covering all required behavior paths (including edge cases like spaced paths, assignment forms, and empty arguments) must exist against untouched production code first. Incomplete coverage passes TDD but fails adversarial review; front-load completeness to avoid rework.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
