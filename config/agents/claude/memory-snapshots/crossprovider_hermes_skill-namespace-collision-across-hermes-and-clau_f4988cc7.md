---
name: crossprovider hermes skill-namespace-collision-across-hermes-and-clau
description: Skill namespace collision across ~/.hermes and .claude directories
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-loading, tool-limitation, namespace-collision]
---

Relative skill names matching files in both `~/.hermes/skills/` and `.claude/skills/` trigger "ambiguous name" errors from skill_view. Non-relative patterns are rejected with "Non-relative patterns are unsupported," leaving no straightforward resolution when the same skill path exists in multiple locations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
