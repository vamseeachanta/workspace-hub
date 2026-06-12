---
name: crossprovider hermes skill-name-ambiguity-fails-without-fallback
description: Skill name ambiguity fails without fallback
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-loading, error-handling, tooling]
---

When a skill name matches in both `~/.hermes/skills/` and repo `.claude/skills/`, skill_view returns an error; no silent fallback. Use relative paths or explicit namespace prefixes. Absolute paths are rejected.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
