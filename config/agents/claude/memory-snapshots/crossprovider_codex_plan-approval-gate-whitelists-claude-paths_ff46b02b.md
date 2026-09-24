---
name: crossprovider codex plan-approval-gate-whitelists-claude-paths
description: Plan-approval gate whitelists .claude/* paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-gate, governance, false-assumption]
---

The `.claude/hooks/plan-approval-gate.sh` enforcement script already whitelists updates to `.claude/skills/`, `.claude/rules/`, and related paths, so onboarding changes to these surfaces do not require pre-approval. Prior assumption that skills edits were blocked was incorrect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
