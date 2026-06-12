---
name: crossprovider gemini broad-safe-path-exemptions-defeat-enforcement-ga
description: Broad safe-path exemptions defeat enforcement gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [governance, gates, security, safe-paths]
---

Whitelisting entire directories (e.g., `.claude/skills/*`) from plan-approval gates can bypass governance if those paths contain implementation rather than config. Exemptions should be narrowly scoped to config-only paths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
