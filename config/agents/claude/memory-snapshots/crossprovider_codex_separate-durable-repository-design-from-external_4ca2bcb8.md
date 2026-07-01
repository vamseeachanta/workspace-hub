---
name: crossprovider codex separate-durable-repository-design-from-external
description: Separate durable repository design from external access layers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [architecture, data-pipelines, design-pattern]
---

When extending data pipelines to new sources, keep materialized datasets (in /mnt/ace or repo storage) separate from access APIs (e.g., PatchOps query layer). Durable design must not depend on external APIs; access layers are optional shortcuts for prototyping or fast lookup, never the primary design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
