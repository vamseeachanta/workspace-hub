---
name: crossprovider hermes provider-spend-forward-dispatch-uses-6h-capacity
description: Provider spend-forward dispatch uses 6h capacity refresh cycles
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-routing, capacity-aware, spend-forward, overnight-dispatch, multi-provider]
---

When provider credits are not bottleneck, refresh capacity telemetry every ~6h and reroute work based on fresh availability. Partition work by gate state (draft/plan-review/plan-approved). Route Claude→control/adversarial-review, Codex→bounded-implementation, Gemini→research/recon. Write durable artifacts (prompts, logs, results) for monitor reconciliation before feeding next wave.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
