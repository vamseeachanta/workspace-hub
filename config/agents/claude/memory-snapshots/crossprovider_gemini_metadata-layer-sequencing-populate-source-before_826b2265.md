---
name: crossprovider gemini metadata-layer-sequencing-populate-source-before
description: Metadata-layer sequencing: populate source before artifacts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, metadata, sequencing]
---

When building knowledge systems (SKILLS_GRAPH.yaml, indexes), populate SKILL.md frontmatter (source of truth) first, then derive consolidated artifacts. Reverse order causes data fragmentation and synchronization overhead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
