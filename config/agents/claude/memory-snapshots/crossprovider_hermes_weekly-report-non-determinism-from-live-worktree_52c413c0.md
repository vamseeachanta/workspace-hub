---
name: crossprovider hermes weekly-report-non-determinism-from-live-worktree
description: Weekly report non-determinism from live worktree state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, reproducibility, time-series-reports]
---

llm-wiki weekly freshness scanner is non-deterministic: re-running for the same date with same code produces different page counts (19953→19954; marine-engineering 19221→19222). Root cause: live repo changes between runs affect counts. Time-series reports must freeze the baseline artifact, not derive it from working-tree state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
