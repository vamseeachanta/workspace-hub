---
name: crossprovider codex skill-validation-gate-use-validate-skill-py-stri
description: Skill validation gate: use validate_skill.py --strict before publication
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [skills, validation, quality-gate]
---

Run `uv run skills/validate_skill.py --strict` to catch YAML frontmatter and structure issues before skills enter review or publication. Integrate this validation into review workflows so malformed SKILL.md files (missing required fields, invalid YAML) are caught early and don't propagate through publication gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
