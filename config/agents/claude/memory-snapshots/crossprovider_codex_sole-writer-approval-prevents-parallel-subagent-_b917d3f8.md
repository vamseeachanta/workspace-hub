---
name: crossprovider codex sole-writer-approval-prevents-parallel-subagent-
description: Sole-writer approval prevents parallel subagent hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [concurrency, subagent-coordination, git-safety]
---

When work is explicitly approved as single-threaded (sole writer), delegating to subagents creates phantom-write risk: subagent reads stale working-tree state, commits to a local branch, main session overwrites or resets without visibility. Keep implementation solo when approval is bound to serialized execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
