---
name: crossprovider codex content-type-routing-precedes-extraction-depth-d
description: Content-type routing precedes extraction depth decisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [content-classification, extraction-workflow, ordering-correctness]
---

Probe content by actual structure (not path), then route by detected type, THEN decide extraction depth and exclusion. Fail-closed on unknown or ambiguous material. This ordering prevents routing conflicts where path-based decisions override content-based trust decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
