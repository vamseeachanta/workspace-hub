---
name: crossprovider gemini knowledge-graph-build-sequence-frontmatter-first
description: Knowledge graph build sequence: frontmatter first, then artifacts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [knowledge-graph, build-pipeline, sequencing, completeness]
---

Correct sequence is: populate SKILL.md frontmatter (all skills) → generate SKILLS_GRAPH.yaml → create category indexes → trim README. Reversing this (graph-first) risks data fragmentation. Full coverage of all skills at each stage prevents partial metadata coverage and orphaned references.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
