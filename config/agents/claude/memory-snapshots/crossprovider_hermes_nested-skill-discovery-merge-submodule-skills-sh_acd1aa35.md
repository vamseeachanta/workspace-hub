---
name: crossprovider hermes nested-skill-discovery-merge-submodule-skills-sh
description: Nested skill discovery: merge-submodule-skills.sh enumerates only top-level
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-discovery, merge-submodule, nesting-gap]
---

Script loops `for skill_dir in skills_dir/*/` (one level only), missing nested SKILL.md files like `digitalmodel/.claude/skills/engineering/orcaflex/SKILL.md` (22+ found in live repo). Plans fixing this must recursively glob `**/.claude/skills/*/SKILL.md` or use `find -name SKILL.md`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
