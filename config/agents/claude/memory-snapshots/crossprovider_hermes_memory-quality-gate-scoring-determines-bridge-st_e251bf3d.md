---
name: crossprovider hermes memory-quality-gate-scoring-determines-bridge-st
description: Memory quality-gate scoring determines bridge strategy
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory, quality-gate, drift-detection, auto-compact]
---

Pre-bridge quality checks: score < 50 = abort (degenerate memory); 50-70 = auto-compact then bridge; >= 70 = bridge directly. Quality failures on duplicates, stale entries, char limits, or missing files block bridging until fixed. High-quality memory ensures durable cross-session knowledge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
