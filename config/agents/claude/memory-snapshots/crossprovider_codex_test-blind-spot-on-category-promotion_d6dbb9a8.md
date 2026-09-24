---
name: crossprovider codex test-blind-spot-on-category-promotion
description: Test blind spot on category promotion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, negative-cases, classification-tests]
---

Tests typically validate happy-path inputs (clean data in correct category) but miss negative cases where a field gets promoted across categories (e.g., support-asset row with candidate extraction_status). Add tests that inject mismatched tuples and verify rejection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
