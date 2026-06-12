---
name: crossprovider hermes skill-path-ambiguity-both-hermes-and-claude-can-
description: Skill path ambiguity: both ~/.hermes and ./.claude can have same skill name
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-loading, path-ambiguity, tooling]
---

When both `/home/$USER/.hermes/skills/path/skill` and `./.claude/skills/path/skill` exist with the same basename, skill loader refuses to guess and demands categorized path (e.g., `autonomous-ai-agents/hermes-agent` not bare `hermes-agent`). This blocks skill loading and requires explicit disambiguiation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
