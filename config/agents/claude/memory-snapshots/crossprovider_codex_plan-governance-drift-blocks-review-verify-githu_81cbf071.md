---
name: crossprovider codex plan-governance-drift-blocks-review-verify-githu
description: Plan governance drift blocks review; verify GitHub labels match local plan status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, governance, codex-pattern]
---

When a draft plan file claims `Status: draft` but GitHub shows `status:plan-approved`, that is unresolvable governance mismatch. Plans citing missing review artifacts (files not on disk) cannot proceed. Always verify the plan's stated status against live GitHub labels and required artifact paths before scoring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
