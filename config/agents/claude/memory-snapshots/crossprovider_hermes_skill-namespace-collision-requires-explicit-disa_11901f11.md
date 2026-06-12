---
name: crossprovider hermes skill-namespace-collision-requires-explicit-disa
description: Skill namespace collision requires explicit disambiguation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-skills, tooling-quirk]
---

When loading skills from dual locations (`~/.hermes/skills/` and repo `.claude/skills/`), ambiguous skill names fail. Absolute paths are rejected by skill_view, so use relative namespacing or explicit disambiguation. This is a constraint during skill-loading in planning/execution workflows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
