---
name: crossprovider gemini skill-architecture-cross-cutting-vs-stage-specif
description: Skill architecture: cross-cutting vs stage-specific content
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skills, architecture, refactoring, organization]
---

When refactoring large skill files into per-stage micro-skills, keep cross-cutting rules (terminology, gate policy, orchestrator patterns) in the main SKILL.md, and route only stage-specific guidance into per-stage micro-skill files. This prevents duplication and keeps the main skill file as a reference source.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
