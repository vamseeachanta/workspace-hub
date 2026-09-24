---
name: crossprovider gemini skill-discovery-via-command-registry-not-skills-
description: Skill discovery via command registry, not skills directory
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skill-system, discovery]
---

Skills are discovered through `.claude/commands/<category>/<name>.md` (not `.claude/skills/`). Command file contains YAML frontmatter (name, description, category) and references the SKILL.md implementation. Command appears in `/skills` list as `<category>:<name>`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
