---
name: tdd-verification-and-adversarial-review
description: Verify pre-written TDD tests pass, conduct adversarial code review on committed diffs, and route findings to existing issues
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["tdd", "testing", "code-review", "verification"]
---

# TDD Verification & Adversarial Review

When inheriting a TDD task where tests were pre-written: (1) Run full test suite to confirm RED→GREEN state and all 496+ tests pass; (2) Examine committed diffs for design choices (quantile logic, boundary conditions, type consistency); (3) Classify findings as MINOR (type annotation, docstring gaps) vs MAJOR (logic errors requiring fix round); (4) Route learnings to existing issues (#1972 for test-coverage gaps) rather than creating noise; (5) Post GitHub comment with verdict and push summary before exit.