---
name: crossprovider hermes artifact-generation-gates-on-code-correctness-ex
description: Artifact generation gates on code correctness + explicit test passage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-generation, test-driven, build-gate]
---

Stale/incorrect artifacts persist even after code fixes; artifact regeneration is not automatic on code change. Tests must explicitly pass before artifact regeneration; no implicit invalidation of prior outputs. Requires conscious 'regenerate-artifacts' step, not triggered by code modification alone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
