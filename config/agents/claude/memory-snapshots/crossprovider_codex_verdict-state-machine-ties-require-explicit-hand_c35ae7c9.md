---
name: crossprovider codex verdict-state-machine-ties-require-explicit-hand
description: Verdict state machine ties require explicit handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verdict-logic, tie-handling, state-machine]
---

When exactly 2 reporters disagree or 4 reporters split 2/2, no strict majority exists; must explicitly define tie verdict (DIVERGES or NO-MAJORITY) before implementation; cannot rely on Counter.most_common(1) input order.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
