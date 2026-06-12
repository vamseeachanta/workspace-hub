---
name: crossprovider hermes skill-tree-fragility-session-start-routine-lost-
description: Skill tree fragility: session-start-routine lost, loaded by Hermes instead
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-tree, fragility, hermes-coupling]
---

session-start-routine is referenced in NEW_SKILLS_SUMMARY.md and cross-agent audit as existing, but the .claude/skills/ file is missing (likely deleted during GSD migration). Hermes loads it dynamically instead of from the skill tree. Same pattern for comprehensive-learning (actively used nightly but not in skill tree). Skill tree divergence from runtime state is a fragility risk.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
