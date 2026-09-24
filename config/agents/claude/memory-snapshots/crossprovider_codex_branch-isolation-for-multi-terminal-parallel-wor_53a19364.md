---
name: crossprovider codex branch-isolation-for-multi-terminal-parallel-wor
description: Branch isolation for multi-terminal parallel work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-strategy, multi-agent, coordination, branching]
---

When multiple agents/terminals work in parallel on the same repo, use feature branches (e.g., feat/1824-test-uplift) instead of main to avoid git lock contention. Establish explicit domain ownership (Terminal 1 owns geotechnical/) to prevent overlapping edits. Push feature branch periodically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
