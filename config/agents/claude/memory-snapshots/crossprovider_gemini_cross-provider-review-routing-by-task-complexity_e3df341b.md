---
name: crossprovider gemini cross-provider-review-routing-by-task-complexity
description: Cross-provider review routing by task complexity (T1/T2/T3)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, review-routing, multi-provider]
---

Plans are routed for multi-provider review based on complexity: T1 (single-file) = Claude only, T2 (multi-file) = Claude + Codex, T3 (large/systemic) = Claude + Codex + Gemini. Plans are not approval-ready until all designated providers return no MAJOR findings. This gates plan approval at the resource-intelligence stage.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
