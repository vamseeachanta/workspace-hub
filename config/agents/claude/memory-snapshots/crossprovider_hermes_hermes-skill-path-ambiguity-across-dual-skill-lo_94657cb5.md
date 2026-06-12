---
name: crossprovider hermes hermes-skill-path-ambiguity-across-dual-skill-lo
description: Hermes skill path ambiguity across dual skill locations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, tooling, skill-loading]
---

Loading `hermes-agent` by bare name fails with ambiguity error when the skill exists in two locations: user home (`~/.hermes/skills/hermes-agent/SKILL.md`) and repo (`.claude/skills/autonomous-ai-agents/hermes-agent/SKILL.md`). Tool refuses to guess. Use categorized path: `autonomous-ai-agents/hermes-agent`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
