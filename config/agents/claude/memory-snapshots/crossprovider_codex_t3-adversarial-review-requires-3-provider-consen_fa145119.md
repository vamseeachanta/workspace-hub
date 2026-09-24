---
name: crossprovider codex t3-adversarial-review-requires-3-provider-consen
description: T3 adversarial review requires 3-provider consensus, timeout degrades to UNAVAILABLE
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-methodology, cross-provider, consensus]
---

Large-scope reviews (T3) require 3 providers (Claude + Codex + Gemini). Single-provider verdict ≠ consensus. When a provider hits timeout boundary (~300s), record as UNAVAILABLE (not auto-downgrade to 2-provider). MAJOR findings hold implementation gate until plan is corrected and re-reviewed by full wave.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
