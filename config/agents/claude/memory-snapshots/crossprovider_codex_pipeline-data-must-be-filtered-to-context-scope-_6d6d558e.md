---
name: crossprovider codex pipeline-data-must-be-filtered-to-context-scope-
description: Pipeline data must be filtered to context scope at every stage
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-pipeline, scoping, testing]
---

When a pipeline accepts context (e.g., field_code parameter), compute derived from that context must be re-scoped at each stage boundary. In multi-field datasets, unscoped pipelines produce incorrect reports silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
