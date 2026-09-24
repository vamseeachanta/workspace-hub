---
name: crossprovider codex breaking-schema-changes-require-migration-strate
description: Breaking schema changes require migration strategy before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, backward-compatibility, data-migration]
---

Proposing data format changes (e.g., replace `skill` field with `target_type`) without upfront migration strategy is a blocking defect. Must inventory existing consumers, choose additive vs breaking, document compatibility window, and add consumer migration tests before implementation. Cannot defer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
