---
name: crossprovider codex dispatcher-path-escape-quarantine-pattern
description: Dispatcher path-escape quarantine pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agent-dispatch, resilience, multi-agent-workflow]
---

When a multi-agent ingest batch produces output outside allowed paths (scripts/, tests/ code), do not crash the entire dispatch run. Instead: catch the path-escape exception, git reset/checkout/clean the worktree to discard rogue output, log a WARNING, and continue to the next chunk. Create PR only if any chunks succeeded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
