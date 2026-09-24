---
name: crossprovider codex workflow-edits-require-regression-tests-for-prio
description: Workflow edits require regression tests for prior-established invariants
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, regression-testing, invariants]
---

When editing a workflow that had a prior fix (e.g., issue #2448 established 'smoke runs before lint/mypy'), the new plan must add regression tests asserting those invariants still hold, not just the new behavior. Workflow re-edits without regressing-prior-fix guards risk reintroducing old blockers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
