---
name: crossprovider hermes pace-expensive-quota-across-time-windows-not-upf
description: Pace expensive quota across time windows, not upfront
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [resource-pacing, quota, overnight-dispatch]
---

For costly operations (Claude), schedule 4 stages at 22:30, 00:30, 02:30, 05:30 across 8-hour sleep window instead of burning quota immediately. Enables parallel fleet execution without rate-limit spikes and lets cheaper agents (Codex) cross-review results.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
