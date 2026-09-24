---
name: crossprovider gemini bidirectional-skill-linking-prevents-knowledge-g
description: Bidirectional skill linking prevents knowledge graph fragmentation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skills-management, metadata, knowledge-graph]
---

Maintain `related_skills` references bidirectionally in skill frontmatter. When adding a relationship between skills, update both skills' `related_skills` lists. Missing reciprocal links cause discovery failures and inconsistent metadata across sessions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
