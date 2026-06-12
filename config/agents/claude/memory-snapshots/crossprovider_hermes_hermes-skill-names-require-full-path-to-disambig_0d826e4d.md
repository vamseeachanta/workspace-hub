---
name: crossprovider hermes hermes-skill-names-require-full-path-to-disambig
description: Hermes skill names require full path to disambiguate across system/user locations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, skill-loading, disambiguation]
---

Bare skill name `hermes-agent` fails when defined in both `~/.hermes/skills/hermes-agent/` and `<repo>/.claude/skills/autonomous-ai-agents/hermes-agent/`; tool refuses to guess. Require full path like `autonomous-ai-agents/hermes-agent` for loading.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
