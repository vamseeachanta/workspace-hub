---
name: crossprovider codex parallel-write-reconciliation-over-force-push
description: Parallel-write reconciliation over force-push
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-safety, concurrency, multi-agent-coordination]
---

When concurrent sessions land commits on the same planning/implementation branch, preserve both and audit independently; never force-push or discard parallel work. Inspect reflog, run multi-agent independent audits of review provenance and contract regressions, then merge only verified content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
