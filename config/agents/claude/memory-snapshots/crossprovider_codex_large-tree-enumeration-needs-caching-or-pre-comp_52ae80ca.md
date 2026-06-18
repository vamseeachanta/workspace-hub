---
name: crossprovider codex large-tree-enumeration-needs-caching-or-pre-comp
description: Large tree enumeration needs caching or pre-computed indices
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [performance, caching, enumeration, scalability]
---

Repeated enumeration of large skills trees (thousands of nested SKILL.md files) hits timeouts in both plan reviews and hot-path code. Use cached metadata or incremental indices instead of filesystem walk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
