---
name: crossprovider codex retention-windows-must-match-claimed-metrics
description: Retention windows must match claimed metrics
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [metrics, retention, accuracy]
---

If a plan claims 90-day health metrics but system only retains 15 days of logs, the metric is false. Must resolve whether 90-day window is achievable or explicitly label it as best-available window in all acceptance criteria and pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
