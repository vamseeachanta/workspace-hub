---
name: crossprovider gemini skill-ecosystem-health-via-staleness-detection-n
description: Skill ecosystem health via staleness detection, not raw counts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, ecosystem-health, knowledge-graph, metrics]
---

Replace arbitrary count thresholds (e.g., 350 total skills, 50 per category) with usage-based staleness (`last_used` timestamps) and metadata completeness (`capabilities:`, `requires:`, `see_also:` frontmatter). Large, well-indexed skill libraries are acceptable; stale and unreferenced skills are the problem. Threshold-based health checks penalize legitimate domain depth.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
