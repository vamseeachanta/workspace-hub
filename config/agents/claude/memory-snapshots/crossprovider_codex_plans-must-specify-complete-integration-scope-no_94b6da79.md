---
name: crossprovider codex plans-must-specify-complete-integration-scope-no
description: Plans must specify complete integration scope, not just happy path
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, data-pipeline, scope]
---

When proposing new data surfaces or content types, explicitly list ALL integration points where they must appear: search indices, discovery surfaces, tooling commands, artifact pipelines. Partial integration (e.g., adding content but forgetting `search-wiki.py` updates) leaves deliverables unachievable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
