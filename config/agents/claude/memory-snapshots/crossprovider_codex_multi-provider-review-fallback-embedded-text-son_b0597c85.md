---
name: crossprovider codex multi-provider-review-fallback-embedded-text-son
description: Multi-provider review fallback: embedded text + Sonnet under 180s timeout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-provider-review, fallback-pattern, timeout-handling]
---

When primary providers timeout (Claude >3min, Codex >5min), fallback to read-only review with complete plan/evidence text embedded in prompt, all tools disabled, Sonnet model, and 180s hard timeout. Converged to reliable pattern across multiple review cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
