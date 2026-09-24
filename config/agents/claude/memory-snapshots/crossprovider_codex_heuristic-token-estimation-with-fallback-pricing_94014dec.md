---
name: crossprovider codex heuristic-token-estimation-with-fallback-pricing
description: Heuristic token estimation with fallback pricing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cost-tracking, heuristics, estimation, resilience]
---

When actual token counts are unavailable, estimate from heuristics: base context (4000 tokens) + per-tool input (2500) + per-script input (500) + output per tool (80). Maintain fallback pricing tables for models when registry unavailable, degrades gracefully.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
