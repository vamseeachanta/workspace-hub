---
name: crossprovider hermes memory-bridge-auto-compaction-gates-prevent-dege
description: Memory bridge auto-compaction gates prevent degenerate memory transfer
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-management, quality-gates, hermes-claude-sync]
---

Hermes→Claude memory bridge uses quality-score thresholds: <50 aborts (degenerate), 50-70 auto-compacts then bridges, >=70 bridges directly. Auto-compaction is key — it removes duplicates and stale entries before transfer, preventing low-signal noise from accumulating in canonical repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
