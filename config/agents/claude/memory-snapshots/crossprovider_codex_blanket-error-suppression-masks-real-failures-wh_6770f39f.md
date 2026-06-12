---
name: crossprovider codex blanket-error-suppression-masks-real-failures-wh
description: Blanket error suppression masks real failures while improving metrics
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, metrics-gaming, hooks, WRK-1016]
---

WRK-1016 proposes `2>/dev/null || true` for slow hooks >2s latency. This hides real hook errors while improving latency metrics, masking governance/safety signals. Requires per-hook diagnosis: profile root cause, then optimize, short-circuit in specific contexts, or document as intentionally best-effort — not blanket suppression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
