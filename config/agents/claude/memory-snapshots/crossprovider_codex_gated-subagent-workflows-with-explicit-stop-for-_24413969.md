---
name: crossprovider codex gated-subagent-workflows-with-explicit-stop-for-
description: Gated subagent workflows with explicit stop-for-review checkpoints
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagent-workflow, gating, verification, deliverables]
---

When delegating to subagents, establish explicit scope gates (e.g., artifact-only constraints blocking implementation/flowcharts) and named stop-for-review checkpoints before proceeding to downstream work. Verify delivered artifacts by reading them back post-write to guard against phantom writes. This pattern enforces controlled delivery and prevents scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
