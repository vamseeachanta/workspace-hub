---
name: crossprovider hermes memory-bridge-quality-gate-and-auto-compaction-w
description: Memory bridge quality gate and auto-compaction workflow
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-system, quality-gate, automation]
---

Memory bridge gates on quality score: score <50 aborts bridging, 50–70 auto-compacts memory then proceeds, >=70 proceeds directly. MEMORY.md index has a 2200-char limit enforced by pre-bridge compaction when approaching threshold; this prevents unbounded index growth.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
