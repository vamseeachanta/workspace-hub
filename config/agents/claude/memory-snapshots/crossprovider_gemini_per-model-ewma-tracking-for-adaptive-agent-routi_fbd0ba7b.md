---
name: crossprovider gemini per-model-ewma-tracking-for-adaptive-agent-routi
description: Per-model EWMA tracking for adaptive agent routing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [routing, model-selection, ewma, adaptive]
---

Track individual model variants (e.g., claude-opus vs claude-sonnet) via tier-specific EWMA ratings, not just per-provider. Cold-start models use default_priority/25 as baseline score, plus +0.3 capability bonus if model tier matches task tier. This captures cost/capability tradeoffs better than binary provider routing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
