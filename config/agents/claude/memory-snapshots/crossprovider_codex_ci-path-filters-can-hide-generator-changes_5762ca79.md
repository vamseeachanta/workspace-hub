---
name: crossprovider codex ci-path-filters-can-hide-generator-changes
description: CI path filters can hide generator changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-cd, workflow, generators]
---

Workflow triggers on output paths (docs/api/**) do not detect changes to generator source (scripts/**) or their fixture inputs (tests/). Both source and fixture paths need explicit declarations in push/pull_request filters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
