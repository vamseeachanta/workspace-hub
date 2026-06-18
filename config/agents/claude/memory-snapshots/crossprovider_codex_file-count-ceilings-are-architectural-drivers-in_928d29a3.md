---
name: crossprovider codex file-count-ceilings-are-architectural-drivers-in
description: File-count ceilings are architectural drivers in llm-wiki
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [architecture, modularity, file-size-constraints, architectural-decisions]
---

#704 matrix generator hit ~399 lines, triggering the data/render/matrix split in #705. This ceiling is an implicit architectural constraint; plans should acknowledge it and justify modularity decisions around it rather than treating refactoring as optional cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
