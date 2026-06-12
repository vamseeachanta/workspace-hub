---
name: crossprovider hermes pace-claude-quota-usage-across-time-windows-over
description: Pace Claude quota usage across time windows; overnight multi-stage jobs preserve budget
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [quota-management, automation, pacing, overnight-work]
---

For overnight/autonomous work with bounded quota, schedule multi-stage jobs across the available window (e.g., 4 stages spread 2h apart) instead of consuming all usage immediately. Self-contained prompts with explicit time/scope limits allow parallel processing while preserving quota for daytime work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
