---
name: crossprovider gemini two-tier-backwards-compatibility-discriminator-f
description: Two-tier backwards-compatibility discriminator for agent gate verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [agent-infrastructure, backwards-compatibility, gate-contract]
---

Gate verification uses WRK id (numeric part after WRK- prefix) as primary discriminator: id < 658 skips gate entirely (legacy exemption), while id ≥ 658 additionally checks created_at timestamp against cutoff (2026-03-09 UTC). Missing, malformed, or non-numeric id fails gate (treat as new). This dual-tier approach prevents breaking pre-658 items on upgrade while enforcing logs for new work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
