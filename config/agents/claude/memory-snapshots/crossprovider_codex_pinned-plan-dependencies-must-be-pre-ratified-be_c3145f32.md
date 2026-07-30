---
name: crossprovider codex pinned-plan-dependencies-must-be-pre-ratified-be
description: Pinned plan dependencies must be pre-ratified before plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [planning, dependencies, validation]
---

When a plan claims correctness by pinning to an external artifact (specification, amendment, related plan), that artifact must already be tracked and approved. Pinning to untracked or MAJOR-blocked sources makes the plan's correctness speculative; implementation fails when the pinned source is still unratified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
