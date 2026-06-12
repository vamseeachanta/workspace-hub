---
name: crossprovider hermes provider-spend-forward-routing-capacity-telemetr
description: Provider spend-forward routing: capacity telemetry every 6 hours, not process count
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-routing, quota-management, throughput-dispatch]
---

When provider credits are not the bottleneck, refresh capacity/usage telemetry ~every 6 hours and spend available quota on plan prep, review, and bounded execution. Do not judge throughput by raw process count or wrapper liveness alone; verify durable output artifacts. Watch for known stall signatures: Codex `Reading additional input from stdin...`, `bwrap: loopback` failures, Gemini `429 RESOURCE_EXHAUSTED`, and Hermes exit-143 after timeouts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
