---
name: crossprovider codex multi-provider-review-gates-degrade-gracefully
description: Multi-provider review gates degrade gracefully
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, gates, multi-provider]
---

When a review provider is unavailable (e.g., Gemini requires interactive auth; Agy lacks credentials), system correctly downgrades T3 → T2 per policy. Document the unavailable lane and use completed reviews rather than substituting unverified verdicts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
