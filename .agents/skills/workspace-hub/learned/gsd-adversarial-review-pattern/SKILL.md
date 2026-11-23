---
name: gsd-adversarial-review-pattern
description: Catch hidden test failures by running adversarial review on sparse-data edge cases before final push
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["testing", "data-validation", "qa", "edge-cases"]
---

# GSD Adversarial Review Pattern

After implementing analytics functions that handle sparse or missing data, run a focused adversarial review on the exact diff before pushing. Specifically: (1) verify test assertions match the actual filter logic (not just fixture coincidence), (2) check for silent failures where data passes validation but shouldn't, (3) re-run full test suite after fixes. This catches TDD precision errors where tests accidentally pass on incomplete fixtures but would fail on real data.