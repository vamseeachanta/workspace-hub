---
name: crossprovider codex owner-approval-in-external-revision-blob-require
description: Owner approval in external revision blob requires separate repository state materialization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [approval-workflow, governance, state-materialization]
---

Approval recorded in a plan file or commit revision is orthogonal to repository governance state. Approval markers must be materialized as issue labels and artifact files. Check both before treating work as approved; use governance files to record approval transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
