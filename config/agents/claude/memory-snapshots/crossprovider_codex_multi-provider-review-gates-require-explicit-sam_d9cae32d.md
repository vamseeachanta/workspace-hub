---
name: crossprovider codex multi-provider-review-gates-require-explicit-sam
description: Multi-provider review gates require explicit same-round consensus when providers are unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, review-consensus, plan-gates, multi-provider]
---

When a review provider (e.g., Gemini) is unavailable, plan status transitions need documented same-round no-MAJOR consensus from all remaining usable providers, not just one. This constraint must be explicit in the plan gate logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
