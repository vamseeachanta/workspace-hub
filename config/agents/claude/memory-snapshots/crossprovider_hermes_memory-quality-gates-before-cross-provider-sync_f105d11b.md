---
name: crossprovider hermes memory-quality-gates-before-cross-provider-sync
description: Memory quality gates before cross-provider sync
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-management, cross-provider-sync, cron-jobs]
---

Hermes→Claude bridge includes drift detection + quality score (0-100): abort <50, auto-compact+bridge 50-70, bridge directly >=70. Prevents corrupted memory from propagating across providers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
