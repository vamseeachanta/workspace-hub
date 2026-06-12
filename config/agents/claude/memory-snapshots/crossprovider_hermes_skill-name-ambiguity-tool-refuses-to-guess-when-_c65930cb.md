---
name: crossprovider hermes skill-name-ambiguity-tool-refuses-to-guess-when-
description: Skill name ambiguity: tool refuses to guess when multiple matches exist
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-resolution, tooling-quirk]
---

Calling a skill by bare name when it exists in multiple locations (e.g., workspace-hub/.claude/skills/... and CAD-DEVELOPMENTS/.claude/skills/...) causes failure; must load by full path or use unambiguous qualifier. No fallback to first match.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
