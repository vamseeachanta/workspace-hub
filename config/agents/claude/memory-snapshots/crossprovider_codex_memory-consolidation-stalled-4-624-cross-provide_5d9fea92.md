---
name: crossprovider codex memory-consolidation-stalled-4-624-cross-provide
description: Memory consolidation stalled: 4,624 cross-provider files staged, 2 indexed
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [memory-system, consolidation, lifecycle-management, observability]
---

Issue #2833 claimed consolidation + pruning would reduce staging files; actual state shows 4,624 Codex/Gemini/Hermes distillations accumulated with only 2 pointers in live indexes. Requires lifecycle tracking (staged/promoted/superseded/rejected/age-slo) before retrieval becomes usable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
