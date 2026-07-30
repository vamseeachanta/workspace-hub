---
name: crossprovider codex gemini-unavailable-across-all-review-rounds-with
description: Gemini unavailable across all review rounds with auth error — environment/tier issue
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [codex, gemini, mcp, authentication, adversarial-review]
---

Gemini returns "unsupported/ineligible-tier authentication error" consistently across r1-r9 adversarial reviews (not transient). Verify: (1) MCP auth is configured for Codex/Gemini, (2) whether Gemini tier matches the review harness expectations, (3) whether other MCP servers have similar auth gaps. This blocks quorum-based review consensus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
