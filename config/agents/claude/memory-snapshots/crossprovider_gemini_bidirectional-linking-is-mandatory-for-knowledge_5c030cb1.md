---
name: crossprovider gemini bidirectional-linking-is-mandatory-for-knowledge
description: Bidirectional linking is mandatory for knowledge graph coherence
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, knowledge-graph, maintenance, integrity]
---

When creating or modifying a skill, existing related skills must be updated with backreferences in their `related_skills:` or `see_also:` frontmatter. This is a required part of skill creation, not post-processing. Failure to maintain bidirectionality degrades discovery and causes the dependency graph to diverge from reality.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
