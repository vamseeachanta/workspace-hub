---
name: crossprovider gemini skill-registration-commands-in-claude-commands-i
description: Skill registration: commands in .claude/commands/, implementations in .claude/skills/
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [project-structure, skills]
---

Skills are discovered via `.claude/commands/<category>/<name>.md` (entry point with YAML frontmatter: name, description, category). The detailed SKILL.md implementation lives in `.claude/skills/<path>/SKILL.md` and is referenced in the command file via `@.claude/skills/<path>/SKILL.md`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
