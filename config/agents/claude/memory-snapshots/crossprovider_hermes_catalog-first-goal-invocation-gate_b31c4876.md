---
name: crossprovider hermes catalog-first-goal-invocation-gate
description: Catalog-first /goal invocation gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [goal-workflow, hermes-routing, planning]
---

Before invoking /goal or planning-goal skills, fetch `.claude/rules/goal-invocation.md`, then GitHub issue #2695 (catalog) and its latest weekly picklist comment. Validate catalog match (Tier 1–2 entry), check `status:plan-approved`, and surface runner allocation mismatches. This gate is load-bearing for multi-agent routing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
