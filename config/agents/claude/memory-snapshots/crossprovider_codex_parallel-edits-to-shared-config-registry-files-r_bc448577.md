---
name: crossprovider codex parallel-edits-to-shared-config-registry-files-r
description: Parallel edits to shared config/registry files require explicit mutual-ordering notes in issue plans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [workflow, coordination, shared-state]
---

Issues #3336 and #3337 both edit `drive-index-registry.yaml`. Without explicit rebase/merge ordering in the plan, the second landing PR will conflict. Pattern: list all issues editing shared mutable files and specify which rebases onto which (e.g., 'second-lander rebases onto first').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
