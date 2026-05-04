---
name: adversarial-code-review-for-committed-diffs
description: Systematic process for reviewing already-committed code changes to catch type inconsistencies, edge cases, and docstring gaps
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["code-review", "quality-assurance", "testing"]
---

# Adversarial Code Review for Committed Diffs

When code is already pushed and tests pass, perform targeted adversarial review: (1) Identify design choices (quantile indexing, boundary conditions, return types), (2) Check for type annotation inconsistencies (e.g., `int` returned in `dict[str, float]`), (3) Test edge cases (empty sets, zero-duration phases, n=2 quantiles), (4) Verify docstring completeness against implementation. Route minor findings to focused GitHub issues rather than requiring a fix round if core logic is sound.