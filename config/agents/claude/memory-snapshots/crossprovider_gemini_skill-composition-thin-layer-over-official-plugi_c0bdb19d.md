---
name: crossprovider gemini skill-composition-thin-layer-over-official-plugi
description: Skill composition: thin layer over official plugins, never re-embed
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skill-composition, architecture, delegation]
---

Wrap official plugins (INDEX.md, portfolio signals) with delegation logic in skills, not reimplementation. Scope to minimal capabilities (L1+L2 steering signal), defer extensions (L3) to separate WRKs. Prevents logic duplication and simplifies maintenance.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
