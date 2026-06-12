---
name: crossprovider hermes multi-agent-commit-serialization-required-for-pa
description: Multi-agent-commit-serialization required for parallel git writes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git, multi-agent]
---

Parallel agents writing to the same git repo must serialize commits via a shared-target manifest pattern; subagents write files only, main session applies commits. Concurrent git operations race and fail.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
