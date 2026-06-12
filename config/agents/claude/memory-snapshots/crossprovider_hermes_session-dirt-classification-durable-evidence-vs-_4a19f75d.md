---
name: crossprovider hermes session-dirt-classification-durable-evidence-vs-
description: Session dirt classification: durable evidence vs. ephemeral
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, artifact-management]
---

Separate generated fixtures (data/*, cache, stats.json, telemetry) from durable evidence (docs/, skill/, harness changes). Preserve unrelated dirt in worktree but never commit unless explicitly classified as evidence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
