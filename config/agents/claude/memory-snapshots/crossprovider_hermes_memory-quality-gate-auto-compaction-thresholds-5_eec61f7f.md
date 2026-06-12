---
name: crossprovider hermes memory-quality-gate-auto-compaction-thresholds-5
description: Memory quality gate auto-compaction thresholds (50/70)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-safety, quality-gate, auto-compaction]
---

Pre-bridge quality scoring uses three-tier gates: <50 = abort (degenerate), 50-70 = auto-compact MEMORY.md char limits then bridge, 70+ = direct bridge. Prevents corrupted memory from being committed. Thresholds are load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
