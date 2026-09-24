---
name: crossprovider gemini engineering-context-auto-loader-by-domain-tags
description: Engineering context auto-loader by domain tags
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [domain-detection, context-optimization, skills, wrk-lifecycle]
---

WRK items carry domain tags (mooring, fatigue, riser, hull, pipeline, etc.) that map to specific skills, design codes, and memory files. Auto-detect via the tag→domain map to load only ~20 relevant skills instead of the full 350+ catalog. Pattern: read WRK frontmatter tags → match domain map → resolve skill paths → discover memory/spec files → output focused context block.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
