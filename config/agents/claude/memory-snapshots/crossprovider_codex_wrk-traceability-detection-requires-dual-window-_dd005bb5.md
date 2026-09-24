---
name: crossprovider codex wrk-traceability-detection-requires-dual-window-
description: WRK traceability detection requires dual-window git inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, shell-scripting, wrk-detection]
---

Checking `git status --porcelain` alone misses work committed during the session. Inspect both uncommitted changes AND recent commits (e.g., `git log --since="12 hours ago"`). Note: 12h window is a heuristic; true session-scoping requires session-start timestamps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
