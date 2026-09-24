---
name: crossprovider gemini thin-consumer-seams-defer-complex-mapping-contra
description: Thin consumer seams defer complex mapping contracts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, scope-boundaries, integration]
---

When integrating downstream consumers, expose minimal surface (lazy exports, no-op functions) and explicitly defer complex mapping/policy to separate issues. Half-implementation accumulates technical debt faster than deferred work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
