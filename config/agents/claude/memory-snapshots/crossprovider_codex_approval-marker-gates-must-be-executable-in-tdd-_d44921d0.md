---
name: crossprovider codex approval-marker-gates-must-be-executable-in-tdd-
description: Approval marker gates must be executable in TDD, not prose-only
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [workflow-gate-discipline, tdd-testability, llm-wiki-dnv]
---

Five consecutive plan reviews (issues #759–#763) found `.planning/plan-approved/<N>.md` markers referenced in plan prose but not wired into the DNV updater entry points or regression tests. Plans state it as a gate, but no RED test fails when the marker is absent—implementation can silently proceed. Wire approval checks into the updater's validation or test preflight, or remove the gate prose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
