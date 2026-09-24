---
name: crossprovider gemini metadata-source-of-truth-ordering-atomic-first-c
description: Metadata source-of-truth ordering: atomic first, consolidated last
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, metadata, source-of-truth]
---

When building metadata layers, update individual atomic records (e.g., SKILL.md frontmatter) before deriving consolidated views (e.g., SKILLS_GRAPH.yaml). Reverse order creates fragmentation risk, manual sync overhead, and incomplete coverage when not all records are updated.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
