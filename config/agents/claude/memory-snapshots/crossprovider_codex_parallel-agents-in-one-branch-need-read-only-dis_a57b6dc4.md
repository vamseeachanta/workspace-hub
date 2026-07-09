---
name: crossprovider codex parallel-agents-in-one-branch-need-read-only-dis
description: Parallel agents in one branch need read-only discovery of active edits
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [parallel-agents, workflow, discovery, coordination]
---

When multiple agents work on related slices (parser, registry, scheduler) in the same feature branch, read-only exploration treats active edits as in-progress and discovers each layer independently, avoiding false 'blocker' claims and enabling clean integration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
