---
name: crossprovider codex sequence-violations-in-multi-stage-pipelines-ide
description: Sequence violations in multi-stage pipelines: identity depends on later definitions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [architecture, correctness, planning]
---

Catch cases where an early stage's hash or case identity depends on coordinate/semantic definitions frozen in a later stage. Identity and foundational semantics must be locked before stages that depend on them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
