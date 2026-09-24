---
name: crossprovider codex generated-readiness-artifacts-drift-from-live-gi
description: Generated readiness artifacts drift from live GitHub state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [staleness, github-state, artifact-freshness]
---

Snapshots of GitHub issue metadata (labels, state) can become stale if regenerated without re-fetching live issue data. Readiness matrices that depend on issue state should refresh their source-issue snapshots as part of the report build, not cache them indefinitely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
