---
name: crossprovider gemini graceful-fallbacks-prevent-script-blockers
description: Graceful fallbacks prevent script blockers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [script-resilience, error-handling]
---

Scripts that hard-depend on external APIs or optional files become critical blockers when assumptions break. Use explicit fallbacks (missing file → 'not available', API failure → cached result or empty set) rather than failing hard.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
