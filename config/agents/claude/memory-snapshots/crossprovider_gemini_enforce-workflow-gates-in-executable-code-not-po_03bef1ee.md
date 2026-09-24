---
name: crossprovider gemini enforce-workflow-gates-in-executable-code-not-po
description: Enforce workflow gates in executable code, not policy alone
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-gates, executable-enforcement, lifecycle-design]
---

Agents consistently skip lifecycle checkpoints (Stage 5 planning) when gates exist only as documented policy. Gates must be enforced in actual entrypoint scripts (e.g., scripts/agents/plan.sh) with fail-closed behavior, not rely on agent discipline to stop and prompt for user interaction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
