---
name: adversarial-code-review-tdd
description: Systematic adversarial review pattern to identify breaking assumptions in already-passing test suites
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["code-review", "TDD", "quality-assurance", "test-driven-development"]
---

# Adversarial Code Review for Passing Tests

When tests pass but implementation may have hidden flaws, conduct adversarial review by: (1) identify sentinel values or default parameters that conflate different states (e.g., `decline_rate=0.0` as both "not set" and "valid input"), (2) check boundary conditions for unjustified constraints (e.g., `b_factor < 1` when b=1 is mathematically valid), (3) distinguish between user intent and implementation convenience. Fix MAJOR findings, add regression tests for edge cases, then re-run full suite before committing.