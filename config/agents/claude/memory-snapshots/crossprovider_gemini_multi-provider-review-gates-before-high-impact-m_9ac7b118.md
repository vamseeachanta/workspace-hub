---
name: crossprovider gemini multi-provider-review-gates-before-high-impact-m
description: Multi-provider review gates before high-impact migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-provider, review-gates, agent-coordination]
---

Migrations affecting multiple agents (Claude, Codex, Gemini) require explicit plan reviews from each provider with verdicts recorded before apply. Gate condition: Claude non-NO_OUTPUT; if Gemini/Codex is NO_OUTPUT, other two must be APPROVE/MINOR. NO unresolved MAJORs. Machine-checkable via timestamp-based result-file matching.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
