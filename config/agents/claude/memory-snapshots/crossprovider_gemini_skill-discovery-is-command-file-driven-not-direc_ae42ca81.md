---
name: crossprovider gemini skill-discovery-is-command-file-driven-not-direc
description: Skill discovery is command-file driven, not directory-driven
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, architecture]
---

Skills appear in `/skills` list via `.claude/commands/<category>/<name>.md` files that reference SKILL.md implementations—not directly from `.claude/skills/` tree. Directory structure is organizational; discovery is command-file based.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
