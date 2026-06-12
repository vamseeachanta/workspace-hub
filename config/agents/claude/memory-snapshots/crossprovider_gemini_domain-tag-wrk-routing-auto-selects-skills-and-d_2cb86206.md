---
name: crossprovider gemini domain-tag-wrk-routing-auto-selects-skills-and-d
description: Domain-tag WRK routing auto-selects skills and design codes
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [context-loading, domain-aware, skill-routing]
---

WRK `tags:` field (mooring, fatigue, hull, pipeline) auto-routes to domain-specific skills and standards (DNV-RP-C203, API RP 2SK). Prevents loading 350-skill catalog; loads ~20 relevant skills only. Skill paths standardized under `.claude/skills/engineering/marine-offshore/<skill>/`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
