---
name: crossprovider codex scope-creep-via-governance-mutations-alongside-t
description: Scope creep via governance mutations alongside technical features
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scope, governance, refactoring]
---

Plans that implement a technical fix (e.g., dispatcher attestation) also modify `.claude/skills/` or prompt behavior, mixing implementation scope with policy/workflow changes. This adjacent scope expansion increases blast radius without justification and complicates dependency analysis.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
