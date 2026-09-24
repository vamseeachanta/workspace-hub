---
name: crossprovider codex model-name-normalization-required-for-cost-log-l
description: Model name normalization required for cost log lookups
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-transformation, cost-tracking, model-registry]
---

Session logs often use short aliases (e.g., `sonnet-4-6`) while configuration uses full model IDs (e.g., `claude-sonnet-4-6`). Cost recomputation and pricing lookups fail without explicit normalization maps covering all in-use aliases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
