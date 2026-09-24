---
name: crossprovider gemini scope-clarity-layer-vs-grandfathered-infrastruct
description: Scope clarity: layer vs. grandfathered infrastructure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scope-management, technical-debt, legacy-code]
---

When adding features atop existing production code, explicitly distinguish what is new (the new layer) from what is legacy behavior. Defer new state-triggered mutations to follow-on issues to avoid scope creep.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
