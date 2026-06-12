---
name: crossprovider hermes provider-telemetry-divergence-requires-reconcili
description: Provider telemetry divergence requires reconciliation before automation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [automation, provider-cost, telemetry]
---

Live quota scripts may report provider state (e.g., Codex 100% remaining) differently from user's external knowledge (e.g., 50% remaining, 24hr expiry). Hermes automation that relies on quota decisions must first reconcile telemetry sources to avoid wasting budget on expired/unavailable credits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
