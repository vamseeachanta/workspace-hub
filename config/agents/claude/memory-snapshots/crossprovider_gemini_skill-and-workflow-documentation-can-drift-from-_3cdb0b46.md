---
name: crossprovider gemini skill-and-workflow-documentation-can-drift-from-
description: Skill and workflow documentation can drift from implementation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [documentation, skills, governance, drift]
---

Skill files (e.g., `.claude/skills/coordination/issue-planning-mode/SKILL.md`) and procedural documentation (CLAUDE.md, AGENTS.md) can fall out of sync with actual behavior, point to nonexistent resources, or contain deprecated stubs. Update and test these together with the governed workflow to prevent agents from following broken instructions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
