---
name: crossprovider codex record-vs-label-as-source-of-truth-is-a-false-di
description: Record vs. label as source-of-truth is a false dichotomy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-machine, github-api, dispatch, divergence]
---

In state machines using both git-tracked records and GitHub labels, choosing one as 'authoritative' does not eliminate the single point of failure — both can diverge or fail independently. Reconciliation between record and label is the actual requirement, not elevation of one over the other.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
