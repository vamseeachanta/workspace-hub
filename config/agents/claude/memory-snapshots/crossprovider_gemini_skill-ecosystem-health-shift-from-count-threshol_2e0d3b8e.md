---
name: crossprovider gemini skill-ecosystem-health-shift-from-count-threshol
description: Skill ecosystem health: shift from count thresholds to staleness
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, health-metrics, staleness]
---

Arbitrary count limits (350 total skills, 50 per category) have no empirical basis. Instead measure staleness via `last_used` timestamp in frontmatter. Requires index quality: `capabilities:`, `tags:`, `related:` frontmatter well-maintained. Launched in WRK-187 (2026-02-19).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
