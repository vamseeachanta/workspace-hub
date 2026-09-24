---
name: crossprovider codex retention-window-metrics-must-be-explicitly-reco
description: Retention window metrics must be explicitly reconciled with log retention policy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, metrics, data-sourcing]
---

Claiming 90-day metrics from 15-day retained logs is uncomputable. Either archive historical logs, downgrade the metric scope, or label output as 'best-available coverage'; never claim long-window metrics from short-window sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
