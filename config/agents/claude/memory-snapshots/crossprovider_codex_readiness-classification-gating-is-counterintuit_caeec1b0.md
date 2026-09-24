---
name: crossprovider codex readiness-classification-gating-is-counterintuit
description: Readiness classification gating is counterintuitive when default changes before blocker issue closes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [readiness-gates, test-coverage, implementation-blocker]
---

Changing a source area's default_classification to 'ready' does not make it actually classify as ready until the linked blocking issue reaches status:implemented. The _classification() function gates on whether the new default is 'ready' AND all linked issues are closed, or defaults to the fallback. Tests must cover both pre-implementation and post-implementation snapshots; marking the default to ready looks correct but fails silently if the blocker is still open.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
