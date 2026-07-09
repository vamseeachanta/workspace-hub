---
name: crossprovider codex review-gates-with-unavailable-providers-need-nam
description: Review gates with unavailable providers need named fallbacks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [review-gates, provider-availability]
---

If a T2 gate requires two independent reviewers and one provider (Gemini) is unavailable, the plan must explicitly name a fallback reviewer or define degraded-mode approval, not just record 'UNAVAILABLE'. Missing a reviewer is not a passing gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
