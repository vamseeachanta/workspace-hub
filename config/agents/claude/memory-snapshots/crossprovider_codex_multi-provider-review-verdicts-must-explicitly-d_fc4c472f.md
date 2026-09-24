---
name: crossprovider codex multi-provider-review-verdicts-must-explicitly-d
description: Multi-provider review verdicts must explicitly document provider unavailability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-provider, review-gates, transparency]
---

When a review provider becomes unavailable (e.g., Gemini quota exhausted), the verdict should explicitly record UNAVAILABLE or downgrade T3→T2, not silently skip the provider and hide the consensus degradation. Otherwise reviewers assume full 3-agent coverage when only 2 providers ran.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
