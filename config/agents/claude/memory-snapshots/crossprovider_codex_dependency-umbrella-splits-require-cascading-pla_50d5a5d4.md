---
name: crossprovider codex dependency-umbrella-splits-require-cascading-pla
description: Dependency umbrella splits require cascading plan updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, planning, issue-graph, contracts]
---

When an umbrella issue is split into sub-issues, all downstream plans that reference the original must be updated to reference the split contracts. Leaving plans that reference the now-split umbrella can hide incomplete understanding of the new contract structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
