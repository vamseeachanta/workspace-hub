---
name: crossprovider codex claude-as-primary-orchestrator-with-narrower-pro
description: Claude as primary orchestrator with narrower provider adapters
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, provider-routing, orchestration]
---

Validated architectural pattern: `.claude` is the thickest control surface and canonical implementation layer, while `.codex` and `.gemini` are thin adapters around the same contract. This pattern already exists in the repo and should be preserved rather than building new framework parity across providers. Recommendation: delegate narrow, bounded tasks to Codex (implementation, review) and Gemini (large-context research), keep orchestration and decision logic in Claude.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
