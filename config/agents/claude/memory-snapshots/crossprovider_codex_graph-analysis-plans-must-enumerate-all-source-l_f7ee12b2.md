---
name: crossprovider codex graph-analysis-plans-must-enumerate-all-source-l
description: Graph analysis plans must enumerate all source locations and define cross-boundary semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [graphs, dependencies, categories, completeness]
---

Dependency graph plans must explicitly list all directories scanned (pending/, working/, blocked/, done/, archive/, archived/) and define how cross-category edges are handled in filtered views. Naive category filtering hides blockers and reports false-ready nodes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
