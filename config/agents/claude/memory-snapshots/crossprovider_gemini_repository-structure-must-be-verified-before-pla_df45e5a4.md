---
name: crossprovider gemini repository-structure-must-be-verified-before-pla
description: Repository structure must be verified before planning
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [repository-structure, verification]
---

Assume repo directory layouts vary (skills may be under `.claude/skills/`, `.claude/agents/`, or `.claude/workflows/` separately). Plans must verify actual paths via `find` or `ls` before pseudocode. Don't assume conventional layouts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
