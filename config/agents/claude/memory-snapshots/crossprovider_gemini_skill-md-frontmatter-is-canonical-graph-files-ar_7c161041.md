---
name: crossprovider gemini skill-md-frontmatter-is-canonical-graph-files-ar
description: SKILL.md frontmatter is canonical; graph files are generated artifacts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [knowledge-graph, architecture, source-of-truth, metadata]
---

Knowledge graph (SKILLS_GRAPH.yaml) should be generated from SKILL.md frontmatter (`capabilities:`, `requires:`, `see_also:` fields), not hand-curated. This prevents dual-write inconsistency and allows the build system to refresh the graph when frontmatter changes. If both are authoritative, divergence becomes inevitable over time.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
