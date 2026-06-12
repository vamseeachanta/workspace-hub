---
name: crossprovider hermes hermes-skill-path-ambiguity-requires-explicit-ca
description: Hermes skill path ambiguity requires explicit categorization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-loading, path-resolution, hermes]
---

Bare skill name `hermes-agent` fails with ambiguity error when the skill exists in multiple directories (`~/.hermes/skills/hermes-agent` and `.claude/skills/autonomous-ai-agents/hermes-agent`). Skill loading requires explicit categorized path (e.g., `autonomous-ai-agents/hermes-agent`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
