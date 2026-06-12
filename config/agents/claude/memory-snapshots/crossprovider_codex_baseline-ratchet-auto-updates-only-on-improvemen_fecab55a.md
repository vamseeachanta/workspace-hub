---
name: crossprovider codex baseline-ratchet-auto-updates-only-on-improvemen
description: Baseline ratchet auto-updates only on improvement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [quality-gates, ratcheting]
---

Baseline-ratchet gates (mypy errors, dep freshness) automatically decrease baseline when actual count drops below it, enabling gradual improvement without manual baseline resets. Violations (count>baseline) still fail, preventing regression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
