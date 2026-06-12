---
name: crossprovider hermes spend-forward-provider-dispatch-maximize-claude-
description: Spend-forward provider dispatch: maximize Claude/Codex/Gemini throughput when credits available
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-routing, dispatch, quota-management, multi-provider, architecture]
---

When provider credits are not the bottleneck, route work across Claude (control-plane synthesis/adversarial review), Codex (implementation/code review), and Gemini (research/standards scans) in parallel lanes with durable artifact output. Safety gates: no self-approval, no implementation before plan-approval, no outreach/mutations from worker lanes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
