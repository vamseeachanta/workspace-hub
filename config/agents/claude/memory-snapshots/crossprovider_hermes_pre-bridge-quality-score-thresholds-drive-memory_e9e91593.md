---
name: crossprovider hermes pre-bridge-quality-score-thresholds-drive-memory
description: Pre-bridge quality score thresholds drive memory-bridge behavior
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-management, quality-gates, hermes]
---

Memory health gate uses: <50 points → abort bridge (degenerate content), 50-70 → auto-compact duplicates/stale entries then bridge, >=70 → bridge directly. Compaction can recover lost Hermes entries without manual merge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
