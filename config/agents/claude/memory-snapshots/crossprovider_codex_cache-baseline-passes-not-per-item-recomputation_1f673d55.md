---
name: crossprovider codex cache-baseline-passes-not-per-item-recomputation
description: Cache baseline passes, not per-item recomputation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance-pattern, caching]
---

When a baseline pass (e.g., full skill-eval sweep) should inform candidate ranking or follow-up work, cache the full baseline result and only re-run individual items for changed files. Avoids per-item subprocess churn and unrelated slowness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
