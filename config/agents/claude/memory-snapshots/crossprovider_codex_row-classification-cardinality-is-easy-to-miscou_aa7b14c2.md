---
name: crossprovider codex row-classification-cardinality-is-easy-to-miscou
description: Row classification cardinality is easy to miscount in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [data, testing, counting]
---

Plan language like "only pre-AI baseline rows" can hide selection errors because row subsets are easy to miscount. Session 5/6: plan said "6 baseline-preserve rows," but only 2 were `pre-ai-baseline-archive`; 4 were `pre-move-baseline-archive`. Implementation tests only covered the 2 live rows, not the full subset. Explicitly name counts per classification and verify test coverage for all subsets, not just live data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
