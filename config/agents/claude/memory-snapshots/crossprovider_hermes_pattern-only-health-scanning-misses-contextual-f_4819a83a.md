---
name: crossprovider hermes pattern-only-health-scanning-misses-contextual-f
description: Pattern-only health scanning misses contextual failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring, health-checks]
---

Health checker scans for 'ERROR' but misses 'uv: not found' warnings that block execution; apparent success hides real blockers. Add contextual signal patterns (not just keywords); distinguish warnings from errors in scanning logic.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
