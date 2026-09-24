---
name: crossprovider codex citations-must-serialize-to-dict-before-appearin
description: Citations must serialize to dict before appearing in workflow output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [citations, serialization, workflow-safety, dataclass-handling]
---

Raw Citation dataclass objects cause workflow result serialization failures. Use `asdict(citation)` when including citations in output structures (e.g., cfg['results']['citations']). This is a structural contract between the citations registry and workflow result consumers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
