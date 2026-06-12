---
name: crossprovider hermes route-cheap-queries-to-existing-paid-subscriptio
description: Route cheap queries to existing paid subscriptions, not external APIs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cost-optimization, routing, providers]
---

'Cheap' and 'quick' routers often leak spend to OpenRouter. If you have multiple paid subscriptions (Anthropic, Copilot, CodeX), route these queries to existing services first (e.g., Copilot gemini-2.5-flash). Avoids unnecessary per-token billing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
