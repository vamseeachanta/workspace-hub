---
name: crossprovider hermes memory-quality-gate-prevents-low-signal-pollutio
description: Memory quality gate prevents low-signal pollution of auto-memory
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-quality, auto-memory, quality-gates]
---

Before bridging Hermes memory to Claude auto-memory, run quality gate checks. Quality score <50 aborts the bridge; 50-70 auto-compacts first then bridges; >=70 proceeds directly. Skipping this gate allows degenerate entries (stale, duplicate, minimal-signal) to pollute the auto-memory store.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
