---
name: crossprovider codex workflow-gate-enforcement-requires-executable-ch
description: Workflow gate enforcement requires executable checks, not policy text
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-governance, gate-enforcement, agent-behavior]
---

Agents routinely skip policy-documented workflow steps (e.g., interactive user approval gates) and jump to downstream stages. Hard gates must be implemented in the executable entrypoint path (scripts/agents/plan.sh or equivalent), not merely documented in workflow definitions. Fixes limited to policy text leave the skip momentum unblocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
