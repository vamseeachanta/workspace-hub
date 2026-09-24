---
name: crossprovider codex index-tracking-with-enumerate-finditer-misaligns
description: Index tracking with enumerate(finditer) misaligns after duplicate filtering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, data-wrangling, index-tracking]
---

Using `enumerate(finditer(...))` to assign indices can cause misalignment with downstream URL/reference mapping when duplicate rows are skipped or filtered. Indices should be recalculated after filtering or tracked through the filter operation to prevent index-reference mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
