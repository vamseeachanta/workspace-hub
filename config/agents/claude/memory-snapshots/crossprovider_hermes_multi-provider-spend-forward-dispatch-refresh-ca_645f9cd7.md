---
name: crossprovider hermes multi-provider-spend-forward-dispatch-refresh-ca
description: Multi-provider spend-forward dispatch: refresh capacity, partition by gate state, route by fit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-provider, quota-management, workflow-dispatch]
---

When provider credits are not the bottleneck, refresh capacity telemetry every ~6 hours before planning next work wave. Partition issues by gate state (draft → review-only, plan-review → review-hardening, plan-approved → implementation). Route: Claude for control-plane synthesis/approval, Codex for bounded implementation/execution, Gemini for research/recon. Write durable artifacts to docs/plans/overnight-prompts/. Limit auto-feed ticks to 1–2 new lanes per cycle to avoid saturation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
