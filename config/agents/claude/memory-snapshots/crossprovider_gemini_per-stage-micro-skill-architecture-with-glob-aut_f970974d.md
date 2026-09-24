---
name: crossprovider gemini per-stage-micro-skill-architecture-with-glob-aut
description: Per-stage micro-skill architecture with glob auto-load
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skills-architecture, stage-contracts, claude-integration]
---

Extract stage-specific rules from monolithic work-queue-workflow/SKILL.md into per-stage `.claude/skills/workspace-hub/stages/stage-NN-*.md` files. Wire start_stage.py to glob-match and auto-load the relevant skill at entry. Reduces SKILL.md bloat and enables modular, stage-scoped guidance.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
