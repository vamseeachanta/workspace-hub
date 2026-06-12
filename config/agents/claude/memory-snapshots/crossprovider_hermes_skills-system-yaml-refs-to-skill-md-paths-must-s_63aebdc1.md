---
name: crossprovider hermes skills-system-yaml-refs-to-skill-md-paths-must-s
description: Skills system: YAML refs to SKILL.md paths must stay in sync
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, refactoring, architecture]
---

Skill eval YAML files reference SKILL.md paths by name. Moving/renaming skills breaks evals silently with no error. Any skill restructuring requires updating all referencing eval YAML files — keep a sync audit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
