---
name: crossprovider gemini partial-technical-fixes-need-tracking-to-surface
description: Partial technical fixes need tracking to surface completion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [technical-debt, testing, maintenance]
---

Skipping 4 of 22 broken tests unblocks CI but leaves 18 failing silently. Partial fixes require explicit tracking (e.g., skip comments linking to issues) so maintainers see when the underlying problem is resolved. Blanket skip entries create invisible technical debt.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
