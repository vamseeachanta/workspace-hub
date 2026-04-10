---
name: adversarial-code-review-and-fix
description: Systematic pattern for catching design flaws in already-passing code through adversarial review, then fixing them with TDD confirmation.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["code-review", "testing", "quality-assurance", "design-patterns"]
---

# Adversarial Code Review and Fix

When code passes all tests but may have design issues: (1) Run tests to establish baseline. (2) Perform adversarial review looking for sentinel value conflicts, overly strict bounds, and API design problems. (3) Document findings as MAJOR/MINOR. (4) Fix findings one at a time, adding new tests for previously-invalid cases. (5) Rerun full suite to confirm no regressions. (6) Commit fixes separately from implementation. This catches issues that functional testing alone misses.