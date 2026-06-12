---
name: crossprovider codex archive-directory-handling-is-incomplete-in-exis
description: Archive directory handling is incomplete in existing tooling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [queue-system, dependency-graph, legacy-compat]
---

Code that computes blocker satisfaction (generate-index.py, dep-graph logic) only scans archive/ but misses legacy archived/ directory in queue systems. This creates blind spots: blocker visibility changes if archive layout is mixed. Dependency and blocker analysis must scan all satisfied-state directories or explicitly document which is canonical.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
