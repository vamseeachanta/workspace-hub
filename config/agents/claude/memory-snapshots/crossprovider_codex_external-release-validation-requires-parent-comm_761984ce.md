---
name: crossprovider codex external-release-validation-requires-parent-comm
description: External release validation requires parent_commit optimistic concurrency
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [verification, external-systems, concurrency, release-validation]
---

When verification spans multiple external systems (e.g., immutable-revision hashing + live-state APIs), intermediate commits can advance state between checks, causing stale data to pass validation. Pin the initial external state as parent_commit, verify it before operations, and confirm head equality after verification completes to prevent race-condition false passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
