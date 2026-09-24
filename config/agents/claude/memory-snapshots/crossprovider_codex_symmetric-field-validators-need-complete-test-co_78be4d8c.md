---
name: crossprovider codex symmetric-field-validators-need-complete-test-co
description: Symmetric field validators need complete test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, regression-prevention]
---

When validating multiple required fields symmetrically, test coverage must exercise all combinations of missing/empty states. Issue #2981 had tests for missing `description` but not empty/blank `name`, leaving regression gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
