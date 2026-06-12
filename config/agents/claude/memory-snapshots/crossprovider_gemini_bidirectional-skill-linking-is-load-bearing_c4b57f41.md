---
name: crossprovider gemini bidirectional-skill-linking-is-load-bearing
description: Bidirectional skill linking is load-bearing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, metadata, knowledge-graph]
---

Skills system requires bidirectional references: when adding a skill's `related_skills:` frontmatter, must grep and update the referenced skills to link back. Forward-only references create orphaned edges in the knowledge graph.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
