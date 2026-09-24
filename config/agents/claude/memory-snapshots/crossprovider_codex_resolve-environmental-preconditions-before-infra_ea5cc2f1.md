---
name: crossprovider codex resolve-environmental-preconditions-before-infra
description: Resolve environmental preconditions before infrastructure changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, planning, preconditions]
---

Plans touching file systems, configs, or repos must settle 'is this git-tracked? what schema enforces it? who owns the data?' BEFORE proposing file moves, additions, or deletions. Open questions about system state are correctness-critical and must be prerequisites, not post-implementation surprises.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
