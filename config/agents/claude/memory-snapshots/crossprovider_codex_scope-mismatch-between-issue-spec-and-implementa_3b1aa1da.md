---
name: crossprovider codex scope-mismatch-between-issue-spec-and-implementa
description: Scope mismatch between issue spec and implementation requires adversarial review
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [code-review, scope, requirements, acceptance-criteria]
---

Sessions 3-4 show PR #3070 (#3060) had implementation that only covered `scripts/` and `config/`, while issue spec explicitly named `skills/agent-library/configs` as scope. Single-pass implementation review missed scope boundary; adversarial review surfaced it. Issue acceptance criteria must drive scope verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
