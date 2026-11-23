---
name: adversarial-test-review-for-sparse-data
description: Detect hidden test failures in sparse/nullable data by identifying secondary filters that create silent failures
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["testing", "data-validation", "sparse-data", "TDD"]
---

# Adversarial Test Review for Sparse Data

When tests pass on fixtures but would fail on real production data with missing fields, identify secondary filters in the implementation that aren't reflected in test assertions. Run the adversarial review by: (1) map all data filters in the implementation, (2) compare against test fixture coverage, (3) construct edge cases where one filter succeeds but a secondary filter fails silently, (4) verify the test actually asserts both conditions, not just the primary one. This pattern catches accidental passes when fixtures happen to be dense in all dimensions.